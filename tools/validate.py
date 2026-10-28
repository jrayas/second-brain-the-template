#!/usr/bin/env python3
"""Vault validator. Reads every rule from _schema/. Terse output; non-zero exit on any error.

Usage: validate.py [--all] [--reports] [--warnings] [--strict] [--root DIR] [--domain SLUG]
  default prints at most 60 error lines
  --reports / --warnings   also list reports / warnings (tag terms used on only one or two notes)
  --domain SLUG            print every override the domain has and the effective properties per type, then exit
  --root DIR               validate another vault (used by the override tests); default is the vault above tools/

Per-domain overrides: next to a default file (types/kb.yaml) an optional folder (types/kb/) holds one override
file per domain (types/kb/maths.yaml). Three verbs: override, add, remove. See the plugin README.
"""
import re, sys, json, subprocess, pathlib, datetime, unicodedata
import yaml

def _opt(name):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
        print('%s needs a value' % name); sys.exit(2)
    return None


ROOT = pathlib.Path(_opt('--root') or pathlib.Path(__file__).resolve().parent.parent).resolve()
SCH = ROOT / '_schema'
ERRORS, REPORTS, WARNINGS = [], [], []
PLANNED, PENDING = set(), [0]
STRICT = '--strict' in sys.argv



def err(msg): ERRORS.append(msg)
def rep(msg): REPORTS.append(msg)
def warn(msg): WARNINGS.append(msg)


def load(p):
    try:
        return yaml.safe_load(p.read_text())
    except Exception as e:
        err('%s: does not parse (%s)' % (p.relative_to(ROOT), str(e).splitlines()[0]))
        return None


# ---------------------------------------------------------------- schema pack
def check_schema():
    reg = load(SCH / 'registry/types.yaml')
    folders = load(SCH / 'registry/folders.yaml')
    load(SCH / 'registry/scope.yaml')
    if not reg: return None
    mods, vocs, types = {}, {}, {}
    for n, f in reg['modules'].items():
        d = load(SCH / f)
        if d is None: continue
        if d.get('module') != n: err('module name mismatch: %s' % f)
        mods[n] = d
    for n, f in reg['vocabularies'].items():
        d = load(SCH / f)
        if d is None: continue
        if d.get('vocabulary') != n: err('vocabulary name mismatch: %s' % f)
        vocs[n] = d
    prefixes = {}
    for n, t in reg['types'].items():
        d = load(SCH / t['file'])
        if d is None: continue
        if d.get('type') != n: err('type name mismatch: %s' % t['file'])
        if not re.fullmatch(r'[A-Z]{2}', t['prefix']): err('bad prefix %s' % t['prefix'])
        if t['prefix'] in prefixes: err('duplicate prefix %s' % t['prefix'])
        prefixes[t['prefix']] = n
        types[n] = d
        for m in d['uses']:
            if m not in mods: err('type %s uses unknown module %s' % (n, m))
        st = d.get('overrides', {}).get('status', {})
        if not st.get('values') or not st.get('default'): err('type %s: status needs values and default' % n)
        for k in d.get('overrides', {}):
            for a in d['overrides'][k]:
                if a not in ('values', 'default', 'required'): err('type %s override %s.%s not allowed' % (n, k, a))
    for fo, ty in (folders.get('folders') or {}).items():
        if ty not in types: err('folder %s maps to unknown type %s' % (fo, ty))
    # property type consistency
    seen = {}
    def props_of(tn):
        out = {}
        for m in types[tn]['uses']:
            for k, v in (mods.get(m, {}).get('properties') or {}).items(): out[k] = dict(v)
        for k, v in (types[tn].get('overrides') or {}).items():
            out.setdefault(k, {}).update(v)
        for k, v in (types[tn].get('properties') or {}).items(): out[k] = dict(v)
        return out
    full, owners = {}, {}
    for tn in types:
        full[tn] = props_of(tn)
        owners[tn] = {}
        for m in types[tn]['uses']:
            for k in (mods.get(m, {}).get('properties') or {}): owners[tn][k] = m
        for k in (types[tn].get('properties') or {}): owners[tn][k] = None
        for k, v in full[tn].items():
            sig = (v.get('type'), v.get('items'))
            if k in seen and seen[k][0] != sig and v.get('type') not in (None,) and seen[k][0][0] is not None:
                err('property %s has different value types (%s vs %s)' % (k, seen[k][1], tn))
            seen.setdefault(k, (sig, tn))
            if v.get('target') and v['target'] not in types: err('%s.%s target %s unknown' % (tn, k, v['target']))
            if v.get('vocabulary') and v['vocabulary'] not in vocs: err('%s.%s vocabulary unknown' % (tn, k))
    for vn, v in vocs.items():
        names = set(v['terms'])
        syn = {}
        for t, d in v['terms'].items():
            for s in (d or {}).get('synonyms', []) or []:
                if s in names: err('vocab %s: synonym %s collides with a term' % (vn, s))
                if s in syn: err('vocab %s: synonym %s used twice' % (vn, s))
                syn[s] = t
    reg_dom = load_domain_registry()
    resolve_domain_values(reg_dom, full)
    check_requires(reg, mods, types)
    check_prefixes(reg, mods, types, full)
    dom = load_domains(reg, mods, vocs, types, full, owners)
    dom['folder'] = reg_dom['folder'] if reg_dom else {d: d for d in dom['domains']}
    # append-only against HEAD. Files that define structure (the registry's types.yaml, the top-level modules and types) are
    # compared by what each type exposes, so a property can move between modules; everything else is compared file by file.
    try:
        for p in list(SCH.rglob('*.yaml')):
            rel = str(p.relative_to(ROOT))
            if STRUCTURAL.match(p.relative_to(SCH).as_posix()): continue
            old = subprocess.run(['git', 'show', 'HEAD:' + rel], cwd=ROOT, capture_output=True, text=True)
            if old.returncode != 0: continue
            o, n = yaml.safe_load(old.stdout), yaml.safe_load(p.read_text())
            cmp_append(o, n, rel, False)
        check_effective_append_only(reg, full)
    except Exception as e:
        err('append-only check failed: %s' % e)
    return dict(reg=reg, mods=mods, vocs=vocs, types=types, full=full, dom=dom)


# ---------------------------------------------------------------- per-domain overrides
CORE = ('type', 'schema', 'id', 'name', 'status', 'domain', 'section', 'level', 'order', 'created', 'modified')
PREFIXED = ('section', 'track')            # values start with "<domain>-"
CHANGE_KEYS = ('values', 'default', 'description')
VALUE_TYPES = ('string', 'integer', 'boolean', 'date', 'datetime', 'url', 'link', 'enum', 'list')
ITEM_TYPES = ('string', 'link', 'url', 'term')


def rel_of(p): return str(p.relative_to(ROOT))


def override_files(file):
    """The override files next to a default file: types/kb.yaml -> types/kb/*.yaml."""
    d = SCH / re.sub(r'\.ya?ml$', '', file)
    return sorted(d.glob('*.yaml')) if d.is_dir() else []


def parse_override(rel, data, kind, name, slug, module_props):
    """Check the shape of a type or module override file. Returns the data when usable, else None."""
    if not isinstance(data, dict): err('%s: an override file must be a map' % rel); return None
    ok = True
    allowed = {'domain', 'override', 'add', 'remove', kind} | ({'sections'} if kind == 'module' else set())
    for k in data:
        if k not in allowed: err('%s: unknown override key %s' % (rel, k)); ok = False
    if 'domain' not in data: err('%s: missing "domain: %s"' % (rel, slug)); ok = False
    elif data['domain'] != slug: err('%s: file is named for domain %s but says %s' % (rel, slug, data['domain'])); ok = False
    if kind in data and data[kind] != name: err('%s: says %s %s but belongs to %s' % (rel, kind, data[kind], name)); ok = False
    named = {}
    def mention(prop, verb):
        nonlocal ok
        if prop in named: err('%s: %s is under both %s and %s; use one verb per property' % (rel, prop, named[prop], verb)); ok = False
        else: named[prop] = verb
    def in_module(prop):
        return module_props is None or prop in module_props
    ov = data.get('override')
    if ov is not None:
        if not isinstance(ov, dict): err('%s: override must be a map' % rel); ok = False; ov = {}
        for prop, ch in ov.items():
            mention(prop, 'override')
            if not isinstance(ch, dict): err('%s: override %s must be a map' % (rel, prop)); ok = False; continue
            if not in_module(prop): err('%s: cannot override %s: module %s has no such property' % (rel, prop, name)); ok = False
            for k in ch:
                if k == 'type': err('%s: an override may not change the type of %s' % (rel, prop)); ok = False
                elif k not in CHANGE_KEYS: err('%s: unknown override key %s.%s (only values, default, description)' % (rel, prop, k)); ok = False
            if 'values' in ch and (not isinstance(ch['values'], list) or not ch['values']):
                err('%s: override %s.values must be a non-empty list' % (rel, prop)); ok = False
    ad = data.get('add')
    if ad is not None:
        if not isinstance(ad, dict): err('%s: add must be a map' % rel); ok = False; ad = {}
        for prop, d in ad.items():
            mention(prop, 'add')
            if not isinstance(d, dict) or d.get('type') not in VALUE_TYPES: err('%s: add %s needs a type (%s)' % (rel, prop, ', '.join(VALUE_TYPES))); ok = False; continue
            if d['type'] == 'list' and d.get('items') not in ITEM_TYPES: err('%s: add %s: a list needs items (%s)' % (rel, prop, ', '.join(ITEM_TYPES))); ok = False
            if d['type'] == 'enum' and not d.get('values'): err('%s: add %s: an enum needs values' % (rel, prop)); ok = False
    rm = data.get('remove')
    if rm is not None:
        if not isinstance(rm, list): err('%s: remove must be a list' % rel); ok = False; rm = []
        for prop in rm:
            mention(prop, 'remove')
            if prop in CORE: err('%s: %s is a core property and cannot be removed' % (rel, prop)); ok = False
            elif not in_module(prop): err('%s: cannot remove %s: module %s has no such property' % (rel, prop, name)); ok = False
    sec = data.get('sections')
    if sec is not None:
        if not isinstance(sec, list) or not sec: err('%s: sections must be a non-empty list' % rel); ok = False
        elif module_props is not None and 'section' not in module_props: err('%s: sections needs module %s to have a section property' % (rel, name)); ok = False
        else:
            for x in sec:
                if not str(x).startswith(slug + '-'): err('%s: section %s must start with %s-' % (rel, x, slug)); ok = False
    return data if ok else None


def default_ok(rel, prop, d):
    """The default of an enum must be one of its values; integers must be whole numbers."""
    t, dv = d.get('type'), d.get('default')
    if dv is None: return
    if t == 'enum' and dv not in (d.get('values') or []): err('%s: default %r of %s is not one of its values' % (rel, dv, prop))
    elif t == 'integer' and (not isinstance(dv, int) or isinstance(dv, bool)): err('%s: default of %s must be a whole number' % (rel, prop))
    elif t == 'boolean' and not isinstance(dv, bool): err('%s: default of %s must be true or false' % (rel, prop))
    elif t == 'list' and not isinstance(dv, list): err('%s: default of %s must be a list' % (rel, prop))


def apply_domain(tn, slug, base, owner, parts):
    """Default properties + a domain's override files (module files first, then the type file). Returns (props, owner)."""
    props = {k: dict(v) for k, v in base.items()}
    owner = dict(owner)
    for rel, kind, name, d in parts:
        scope = lambda k: k in props and (kind == 'type' or owner.get(k) == name)
        where = '' if kind == 'type' else ' from module %s' % name
        for prop in d.get('remove') or []:
            if not scope(prop): err('%s: cannot remove %s: type %s has no such property%s' % (rel, prop, tn, where))
            else: del props[prop]
        changed = []
        for prop, ch in (d.get('override') or {}).items():
            if not scope(prop): err('%s: cannot override %s: type %s has no such property%s' % (rel, prop, tn, where)); continue
            t = props[prop]
            if 'values' in ch:
                if t.get('type') != 'enum': err('%s: %s is not an enum, so it has no values to change' % (rel, prop))
                else:
                    t['values'] = list(ch['values'])
                    if prop in PREFIXED:
                        for v in ch['values']:
                            if not str(v).startswith(slug + '-'): err('%s: %s value %s must start with %s-' % (rel, prop, v, slug))
            if 'default' in ch: t['default'] = ch['default']
            if 'description' in ch: t['description'] = ch['description']
            if 'values' in ch or 'default' in ch: changed.append((prop, t))
        if d.get('sections'):
            t = props.get('section')
            if not t or owner.get('section') != name or t.get('type') != 'enum': err('%s: sections needs module %s to have an enum section property' % (rel, name))
            else:
                vals = list(t.get('values') or [])
                for x in d['sections']:
                    if x in vals: err('%s: section %s is already in the default list; the default wins, so remove it here' % (rel, x))
                    else: vals.append(x)
                t['values'] = vals
        for prop, t in changed: default_ok(rel, prop, t)   # once the whole file is applied: a default may be one of its sections
        for prop, nd in (d.get('add') or {}).items():
            if prop in props: err('%s: cannot add %s: type %s already has it (use override)' % (rel, prop, tn)); continue
            default_ok(rel, prop, nd)
            if nd.get('type') == 'list' and nd.get('items') == 'term' and nd.get('vocabulary') not in S_VOCS:
                err('%s: added property %s needs a known vocabulary' % (rel, prop))
            props[prop] = dict(nd); owner[prop] = name if kind == 'module' else None
    return props, owner


S_VOCS = {}


def load_domains(reg, mods, vocs, types, full, owners):
    """Read every override file; check it; build the effective properties and vocabularies per (domain, type)."""
    global S_VOCS
    S_VOCS = vocs
    domains = []
    for tn in types:
        for v in (full[tn].get('domain') or {}).get('values') or []:
            if v not in domains: domains.append(v)
    found = {}   # slug -> {'types': {}, 'modules': {}, 'vocs': {}}
    def bucket(slug): return found.setdefault(slug, {'types': {}, 'modules': {}, 'vocs': {}})
    orphans = []
    def known(slug, rel):
        if slug in domains: return True
        if not domains: orphans.append(rel); return False
        err('%s: "%s" is not one of the domains (%s)' % (rel, slug, ', '.join(domains)))
        return False
    for tn, t in reg['types'].items():
        if tn not in types: continue
        for p in override_files(t['file']):
            rel = rel_of(p)
            if not known(p.stem, rel): continue
            d = load(p)
            if d is None: continue
            d = parse_override(rel, d, 'type', tn, p.stem, None)
            if d is not None: bucket(p.stem)['types'][tn] = (rel, d)
    for mn, f in reg['modules'].items():
        if mn not in mods: continue
        mprops = set(mods[mn].get('properties') or {})
        for p in override_files(f):
            rel = rel_of(p)
            if not known(p.stem, rel): continue
            d = load(p)
            if d is None: continue
            d = parse_override(rel, d, 'module', mn, p.stem, mprops)
            if d is not None: bucket(p.stem)['modules'][mn] = (rel, d)
    if orphans: err('%s: %d override file(s) found, but no domains are defined. List them in registry/domains.yaml, or check that the module with the domain property still has its content' % (orphans[0], len(orphans)))
    prefixed_vocs = {v.get('vocabulary') for tn in types for k, v in full[tn].items() if k in PREFIXED and v.get('type') == 'list'}
    for vn, f in reg['vocabularies'].items():
        if vn not in vocs: continue
        base = vocs[vn]
        names = {w.lower() for t, dd in base['terms'].items() for w in [t] + list((dd or {}).get('synonyms') or [])}
        for p in override_files(f):
            rel = rel_of(p)
            if not known(p.stem, rel): continue
            d = load(p)
            if d is None: continue
            if not isinstance(d, dict): err('%s: an override file must be a map' % rel); continue
            bad = [k for k in d if k not in ('domain', 'terms', 'vocabulary')]
            for k in bad: err('%s: unknown override key %s' % (rel, k))
            if 'domain' not in d: err('%s: missing "domain: %s"' % (rel, p.stem))
            elif d['domain'] != p.stem: err('%s: file is named for domain %s but says %s' % (rel, p.stem, d['domain']))
            if not isinstance(d.get('terms'), dict): err('%s: needs a terms map' % rel); continue
            mine, good = {}, True
            for term, dd in d['terms'].items():
                words = [term] + list((dd or {}).get('synonyms') or [])
                clash = next((w for w in words if str(w).lower() in names), None)
                if clash is not None:
                    err('%s: "%s" is already a term or synonym in the default %s vocabulary; the default wins, so remove it here' % (rel, clash, vn)); good = False; continue
                if vn in prefixed_vocs and not str(term).startswith(p.stem + '-'):
                    err('%s: term %s must start with %s-' % (rel, term, p.stem)); good = False
                dup = next((w for w in words if str(w).lower() in mine and mine[str(w).lower()] != term), None)
                if dup is not None: err('%s: "%s" is used for two terms' % (rel, dup)); good = False; continue
                for w in words: mine[str(w).lower()] = term
            if d['domain'] == p.stem and not bad: bucket(p.stem)['vocs'][vn] = (rel, d, good)
    eff, effvoc = {}, {}
    for slug, b in found.items():
        for vn, (rel, d, good) in b['vocs'].items():
            terms = dict(vocs[vn]['terms'])
            base_names = {w.lower() for t, dd in vocs[vn]['terms'].items() for w in [t] + list((dd or {}).get('synonyms') or [])}
            for term, dd in d['terms'].items():
                if not any(str(w).lower() in base_names for w in [term] + list((dd or {}).get('synonyms') or [])): terms[term] = dd
            effvoc[(slug, vn)] = terms
        for tn, t in types.items():
            parts = [(b['modules'][m][0], 'module', m, b['modules'][m][1]) for m in t['uses'] if m in b['modules']]
            if tn in b['types']: parts.append((b['types'][tn][0], 'type', tn, b['types'][tn][1]))
            if parts: eff[(slug, tn)] = apply_domain(tn, slug, full[tn], owners[tn], parts)[0]
    # a property keeps one value type across all types and all domains
    seen = {}
    for tn in types:
        for k, v in full[tn].items(): seen.setdefault(k, ((v.get('type'), v.get('items')), tn))
    for (slug, tn), props in eff.items():
        for k, v in props.items():
            sig = (v.get('type'), v.get('items'))
            if k in seen and seen[k][0] != sig and sig[0] is not None and seen[k][0][0] is not None:
                err('property %s has different value types (%s vs %s, domain %s)' % (k, seen[k][1], tn, slug))
            seen.setdefault(k, (sig, '%s/%s' % (tn, slug)))
            if v.get('target') and v['target'] not in types: err('%s.%s (domain %s) target %s unknown' % (tn, k, slug, v['target']))
    return dict(domains=domains, found=found, eff=eff, effvoc=effvoc)


def load_domain_registry():
    """registry/domains.yaml: the domains, registered like types (prefix and folder optional). None when there is no file."""
    p = SCH / 'registry/domains.yaml'
    if not p.exists(): return None
    rel = rel_of(p)
    d = load(p)
    if d is None: return None
    if not isinstance(d, dict) or not isinstance(d.get('domains'), dict) or not d['domains']:
        err('%s: needs a domains map listing at least one domain' % rel); return None
    names, prefix, folder, pown, fown = [], {}, {}, {}, {}
    for name, v in d['domains'].items():
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', str(name)): err('%s: domain %s must be lowercase letters, digits and single hyphens' % (rel, name)); continue
        if v is not None and not isinstance(v, dict): err('%s: domain %s must be a map such as { prefix: MA }' % (rel, name)); continue
        v = v or {}
        for k in v:
            if k not in ('prefix', 'folder', 'description'): warn('%s: domain %s: unknown attribute %s' % (rel, name, k))
        pre = v.get('prefix')
        if pre is not None:
            if not (isinstance(pre, str) and re.fullmatch(r'[A-Z]{2}', pre)): err('%s: the prefix for %s must be two capital letters' % (rel, name))
            elif pre in pown: err('%s: %s and %s both use the prefix %s' % (rel, pown[pre], name, pre))
            else: pown[pre] = name; prefix[name] = pre
        fo = v.get('folder', name)
        if not isinstance(fo, str) or not fo.strip() or '/' in fo or '\\' in fo: err('%s: the folder for %s must be one folder name, without a slash' % (rel, name)); fo = name
        fo = fo.strip()
        key = ''.join(c for c in unicodedata.normalize('NFD', fo) if not unicodedata.combining(c)).lower()
        if key in fown: err('%s: %s and %s both use the folder %s' % (rel, fown[key], name, fo))
        else: fown[key] = name
        folder[name] = fo
        names.append(name)
    if not names: return None
    default = d.get('default')
    if default is None: default = names[0]
    elif default not in names: err('%s: default must be one of the listed domains (found %s)' % (rel, default)); default = names[0]
    return dict(names=names, prefix=prefix, folder=folder, default=default)


def resolve_domain_values(reg_dom, full):
    """A property with values_from: domains takes its values, default and prefixes from the registry."""
    missing = False
    for tn in full:
        for k, v in full[tn].items():
            if v.get('values_from') != 'domains': continue
            if reg_dom is None: missing = True; continue
            if v.get('prefixes') is not None: err('%s takes its values from registry/domains.yaml, so prefixes belong there' % k)
            v['values'] = list(reg_dom['names'])
            if 'default' not in v: v['default'] = reg_dom['default']
            if reg_dom['prefix']: v['prefixes'] = dict(reg_dom['prefix'])
            else: v.pop('prefixes', None)
    if missing: err('a property takes its values from registry/domains.yaml, which does not exist')


def check_requires(reg, mods, types):
    """A module may name modules a type must also list under uses. A module file must have properties."""
    for mn, m in mods.items():
        if not m.get('properties'): err('%s: module %s has no properties' % ('_schema/' + reg['modules'][mn], mn))
        for need in m.get('requires') or []:
            if need not in reg['modules']: err('%s: module %s requires %s, which is not in the registry' % ('_schema/' + reg['modules'][mn], mn, need))
    for tn, t in types.items():
        for m in t['uses']:
            for need in (mods.get(m, {}).get('requires') or []):
                if need not in t['uses']: err('type %s: module %s requires %s: add it to uses' % (tn, m, need))


def check_prefixes(reg, mods, types, full):
    """The domain property may declare a two-letter prefix per value (used by unique_id): TYPE-DOMAIN-YEAR-NNNN."""
    for mn, f in reg['modules'].items():
        d = (mods.get(mn, {}).get('properties') or {}).get('domain')
        pre = (d or {}).get('prefixes')
        if pre is None: continue
        rel = 'schema/' + f
        if not isinstance(pre, dict): err('%s: domain prefixes must map each value to two capital letters' % rel); continue
        owner = {}
        for k, v in pre.items():
            if not isinstance(v, str) or not re.fullmatch(r'[A-Z]{2}', v): err('%s: the prefix for %s must be two capital letters' % (rel, k)); continue
            if d.get('values') and k not in d['values']: err('%s: %s has a prefix but is not one of the domain values' % (rel, k)); continue
            if v in owner: err('%s: %s and %s both use the prefix %s' % (rel, owner[v], k, v)); continue
            owner[v] = k
    for tn in types:
        if 'unique_id' in full[tn] and not (full[tn].get('domain') or {}).get('prefixes'):
            err('type %s has a unique_id property, so its domain property needs prefixes' % tn)


STRUCTURAL = re.compile(r'^(registry/types\.yaml|modules/[^/]+\.yaml|types/[^/]+\.yaml)$')
SEMANTIC = ('type', 'items', 'required', 'default', 'values', 'min', 'max', 'pattern', 'vocabulary', 'target', 'strict', 'normalise',
            'locked', 'immutable', 'generated', 'managed_by', 'position', 'allow_heading')   # not `description`: documentation only


def head_yaml(rel):
    r = subprocess.run(['git', 'show', 'HEAD:' + rel], cwd=ROOT, capture_output=True, text=True)
    return yaml.safe_load(r.stdout) if r.returncode == 0 else None


def vtuple(v):
    try: return tuple(int(x) for x in str(v).split('.'))
    except Exception: return (0,)


def check_effective_append_only(reg, full):
    """Nothing a type exposes may be removed or changed; values only grow. Where a property is defined does not matter."""
    reg_h = head_yaml('_schema/registry/types.yaml')
    if not isinstance(reg_h, dict): return
    path = '_schema/registry/types.yaml'
    if reg_h.get('format') != reg.get('format'): err('%s: format changed' % path)
    if vtuple(reg.get('min_plugin_version')) < vtuple(reg_h.get('min_plugin_version')): err('%s: min_plugin_version lowered' % path)
    for sect in ('modules', 'vocabularies'):
        for n in reg_h.get(sect) or {}:
            if n not in (reg.get(sect) or {}): err('%s: %s %s removed' % (path, sect[:-1], n))
    mods_h = {n: head_yaml('_schema/' + f) or {} for n, f in (reg_h.get('modules') or {}).items()}
    hd = head_yaml('_schema/registry/domains.yaml')
    head_dom = None
    if isinstance(hd, dict) and isinstance(hd.get('domains'), dict) and hd['domains']:
        hn = list(hd['domains'])
        head_dom = dict(names=hn, default=hd.get('default') if hd.get('default') in hn else hn[0])
    for tn, th_reg in (reg_h.get('types') or {}).items():
        now_reg = (reg.get('types') or {}).get(tn)
        if now_reg is None: err('%s: type %s removed' % (path, tn)); continue
        for k in ('prefix', 'version'):
            if now_reg.get(k) != th_reg.get(k): err('%s: type %s %s changed from %r to %r' % (path, tn, k, th_reg.get(k), now_reg.get(k)))
        th = head_yaml('_schema/' + th_reg['file'])
        if not isinstance(th, dict) or tn not in full: continue
        old = {}
        for m in th.get('uses') or []:
            for k, v in ((mods_h.get(m) or {}).get('properties') or {}).items(): old[k] = dict(v)
        for k, v in (th.get('overrides') or {}).items(): old.setdefault(k, {}).update(v)
        for k, v in (th.get('properties') or {}).items(): old[k] = dict(v)
        for oa in old.values():   # the baseline's own registry resolves values_from: domains, as the current one does
            if oa.get('values_from') == 'domains' and head_dom:
                oa['values'] = list(head_dom['names'])
                if 'default' not in oa: oa['default'] = head_dom['default']
        for prop, oa in old.items():
            na = full[tn].get(prop)
            if na is None: err('type %s: property %s removed' % (tn, prop)); continue
            for k in SEMANTIC:
                ov, nv = oa.get(k), na.get(k)
                if k == 'values' and isinstance(ov, list) and isinstance(nv, list):
                    if nv[:len(ov)] != ov and not set(ov) <= set(nv): err('type %s: property %s: values removed or changed' % (tn, prop))
                    continue
                if k == 'default' and ov is None and na.get('values_from') == 'domains': continue   # the registry supplies the default
                if ov != nv: err('type %s: property %s: %s changed from %r to %r' % (tn, prop, k, ov, nv))


def cmp_append(o, n, path, in_terms):
    if isinstance(o, dict):
        if not isinstance(n, dict): err('%s: changed type' % path); return
        for k, v in o.items():
            if k not in n: err('%s: %s removed' % (path, k)); continue
            cmp_append(v, n[k], path + '.' + str(k), in_terms or k == 'terms')
        for k in n:
            if k not in o and not in_terms: err('%s: new attribute %s' % (path, k))
    elif isinstance(o, list):
        if not isinstance(n, list): err('%s: changed type' % path); return
        if path.endswith('.values') or path.endswith('.synonyms') or path.endswith('.exclude'):
            if n[:len(o)] != o and not set(o) <= set(n): err('%s: values removed or changed' % path)
        elif o != n: err('%s: list changed' % path)
    else:
        if o != n: err('%s: %r changed to %r' % (path, o, n))


# ---------------------------------------------------------------- notes
FM = re.compile(r'^---\n(.*?)\n---\n', re.S)
WL = re.compile(r'\[\[([^\]\|#]+)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]')
BAD_NAME = re.compile(r'[/\\:*?"<>|]|[. ]$|^(CON|PRN|AUX|NUL|COM\d|LPT\d)$', re.I)


def strip_code(t):
    t = re.sub(r'```.*?```', '', t, flags=re.S)
    return re.sub(r'`[^`\n]*`', '', t)


def check_notes(S):
    reg, mods, vocs, types, full, dom = S['reg'], S['mods'], S['vocs'], S['types'], S['full'], S['dom']
    tag_uses = {}
    folders = load(SCH / 'registry/folders.yaml')['folders']
    f2t = dict(folders)
    domains = set(dom['domains'])
    sections = set(mods['curriculum']['properties']['section']['values'])
    tags = set(vocs['tags']['terms']); tracks = set(vocs['tracks']['terms'])
    # domain files
    for d in domains:
        f = ROOT / '.claude/domains' / (d + '.md')
        if not f.exists(): err('missing domain file %s' % f.relative_to(ROOT))
        elif re.search(r'<(slug|domain|section|name)>', f.read_text()): err('%s has an unfilled placeholder' % f.name)
    for s in sections:
        if s.split('-')[0] not in domains: err('section %s does not start with a domain' % s)
    for t in tracks:
        if t.split('-')[0] not in domains: err('track %s does not start with a domain' % t)
    ids_ledger = json.loads((ROOT / '_meta/ids.json').read_text()) if (ROOT / '_meta/ids.json').exists() else {}
    notes = {}
    files = []
    for root in folders:
        base = ROOT / root
        if base.exists(): files += sorted(base.rglob('*.md'))
    names, seen_ids, seen_uids = {}, {}, {}
    parsed = []
    for p in files:
        rel = str(p.relative_to(ROOT))
        txt = p.read_text()
        m = FM.match(txt)
        if not m: err('%s: no frontmatter' % rel); continue
        try:
            fm = yaml.safe_load(m.group(1))
        except Exception as e:
            err('%s: frontmatter does not parse' % rel); continue
        keys = re.findall(r'^([A-Za-z_]+):', m.group(1), re.M)
        name = p.stem
        if name in names: err('%s: file name not unique (also %s)' % (rel, names[name]))
        names[name] = rel
        parsed.append((p, rel, txt, m, fm, keys, name))
    allnames = set(names)
    word_counts = {}
    incoming = {n: 0 for n in allnames}
    secorder = {}
    for p, rel, txt, m, fm, keys, name in parsed:
        parts = p.relative_to(ROOT).parts
        tn = fm.get('type')
        if tn not in types: err('%s: unknown type %r' % (rel, tn)); continue
        if f2t.get(parts[0]) != tn: err('%s: folder maps to %s but type is %s' % (rel, f2t.get(parts[0]), tn))
        if len(parts) != 3 or parts[1] != dom['folder'].get(fm.get('domain'), fm.get('domain')): err('%s: must sit directly in %s/<domain>/' % (rel, parts[0]))
        if fm.get('schema') != reg['types'][tn]['version']: err('%s: schema version' % rel)
        if fm.get('name') != name: err('%s: name does not equal file name' % rel)
        if BAD_NAME.search(name): err('%s: invalid file name' % rel)
        pf = reg['types'][tn]['prefix']
        idv = str(fm.get('id', ''))
        if not re.fullmatch(pf + r'-\d{4}-\d{4,}', idv): err('%s: bad id %s' % (rel, idv))
        else:
            if idv in seen_ids: err('%s: duplicate id (also %s)' % (rel, seen_ids[idv]))
            seen_ids[idv] = rel
            yr = idv.split('-')[1]
            if str(fm.get('created', ''))[:4] != yr: err('%s: id year differs from created' % rel)
            if int(idv.split('-')[2]) > ids_ledger.get(pf, {}).get(yr, 0): err('%s: id beyond ledger' % rel)
        dn = fm.get('domain')
        props = dom['eff'].get((dn, tn), full[tn])
        # the domain-level unique ID: TYPE-DOMAIN-YEAR-NNNN, naming the note's type and domain
        if 'unique_id' in props:
            dpre = ((props.get('domain') or {}).get('prefixes') or {}).get(dn)
            uid = fm.get('unique_id')
            if dpre:
                if uid in (None, ''): err('%s: missing unique_id (domain %s)' % (rel, dn))
                else:
                    um = re.fullmatch(r'([A-Z]{2})-([A-Z]{2})-(\d{4})-(\d{4,})', str(uid))
                    if um:
                        if um.group(1) != reg['types'][tn]['prefix'] or um.group(2) != dpre:
                            err('%s: unique_id %s does not match type %s and domain %s (%s-%s)' % (rel, uid, tn, dn, reg['types'][tn]['prefix'], dpre))
                        if int(um.group(4)) > ids_ledger.get('%s-%s' % (um.group(1), um.group(2)), {}).get(um.group(3), 0): err('%s: unique_id beyond ledger' % rel)
                        if uid in seen_uids: err('%s: duplicate unique_id %s (also %s)' % (rel, uid, seen_uids[uid]))
                        seen_uids.setdefault(uid, rel)
            elif uid not in (None, ''): err('%s: unique_id present but domain %s has no prefix' % (rel, dn))
        ntags = set(dom['effvoc'].get((dn, 'tags'), vocs['tags']['terms']))
        ntracks = set(dom['effvoc'].get((dn, 'tracks'), vocs['tracks']['terms']))
        for k in keys:
            if k in props: continue
            if k in full[tn]: err('%s: property %s is removed for domain %s' % (rel, k, dn))
            else: err('%s: property %s not in schema' % (rel, k))
        if 'breadcrumb' in keys: err('%s: breadcrumb present' % rel)
        for k, v in props.items():
            if (v.get('required') and k not in fm):
                err('%s: missing required %s' % (rel, k))
        # order
        schema_order = [k for k in props if k not in ('created', 'modified')]
        pos = [schema_order.index(k) for k in keys if k in schema_order]
        if pos != sorted(pos): err('%s: property order' % rel)
        if keys[-2:] != ['created', 'modified']: err('%s: created and modified must be last' % rel)
        for k, val in fm.items():
            if k in props: check_value(rel, k, val, props[k], ntags, ntracks, types, allnames, f2t, names, parsed)
        # extra rules
        if str(fm.get('created')) > str(fm.get('modified')): err('%s: created after modified' % rel)
        if fm.get('status') == 'published': err('%s: status published' % rel)
        if fm.get('verified') is True or fm.get('answer_verified') is True: err('%s: verified true' % rel)
        if fm.get('ai_generated') is not True: err('%s: ai_generated must be true' % rel)
        if fm.get('generated_by') != 'claude-code': err('%s: generated_by' % rel)
        if len(str(fm.get('description', ''))) > 160: err('%s: description over 160' % rel)
        secvals = (props.get('section') or {}).get('values') or sections
        if fm.get('section') not in secvals: err('%s: unknown section' % rel)
        elif not str(fm['section']).startswith(str(fm.get('domain')) + '-'): err('%s: section prefix' % rel)
        for t in fm.get('track') or []:
            if not str(t).startswith(str(fm.get('domain')) + '-'): err('%s: track prefix' % rel)
        for k, a in props.items():
            if a.get('type') == 'list' and a.get('items') == 'term' and a.get('vocabulary') == 'tags':
                for t in fm.get(k) or []: tag_uses.setdefault(t, []).append(name)
        key = (fm.get('section'), fm.get('order'))
        if key in secorder: err('%s: order %s duplicated in section (also %s)' % (rel, fm.get('order'), secorder[key]))
        secorder[key] = rel
        body = txt[m.end():]
        if re.search(r'\$|\\\\?\w', m.group(1)) and '$' in m.group(1): err('%s: $ in frontmatter' % rel)
        for h in re.findall(r'^#+ .*$', body, re.M):
            if '$' in h or '\\' in h: err('%s: math in heading' % rel)
        sb = strip_code(body)
        if sb.count('$$') % 2: err('%s: unbalanced $$' % rel)
        if tn in ('exercise', 'scenario'):
            if not re.search(r'^> \[![a-z]+\]-', body, re.M): err('%s: no collapsed answer callout' % rel)
        if tn == 'scenario':
            for c in ('question', 'info', 'failure', 'tip'):
                if not re.search(r'^> \[!%s\]-' % c, body, re.M): err('%s: scenario missing %s callout' % (rel, c))
            if not str(fm.get('senior_signal', '')).strip(): err('%s: senior_signal empty' % rel)
        # inline $: no stray single dollars unless balanced per paragraph
        noblock = re.sub(r'\$\$.*?\$\$', '', sb, flags=re.S)
        for para in re.split(r'\n\s*\n', noblock):
            if para.count('$') % 2: err('%s: unbalanced inline $ in "%s"' % (rel, para.strip()[:30])); break
        # links
        for l in set(WL.findall(m.group(1) + '\n' + body)):
            l = l.strip()
            if l not in allnames:
                if l in PLANNED and not STRICT: PENDING[0] += 1
                else: err('%s: unresolved link [[%s]]' % (rel, l))
            elif l != name: incoming[l] += 1
        word_counts[name] = len(body.split())
        notes[name] = fm
    # companion reciprocity
    for n, fm in notes.items():
        c = fm.get('companion')
        if c:
            c = re.sub(r'[\[\]"]', '', str(c))
            if c in notes:
                back = re.sub(r'[\[\]"]', '', str(notes[c].get('companion') or ''))
                if back != n: err('%s: companion not reciprocal with %s' % (n, c))
    # visuals
    for n, fm in notes.items():
        if fm.get('type') == 'visual':
            f = ROOT / str(fm.get('file'))
            if not f.exists(): err('%s: html file missing' % n)
            if fm.get('kind') == 'calculator' and not fm.get('formula_source'): err('%s: calculator needs formula_source' % n)
    for d in domains:
        hd = ROOT / 'Visuals' / d / 'html'
        stubs = {str(f.get('file')) for f in notes.values() if f.get('type') == 'visual'}
        if hd.exists():
            for h in hd.glob('*.html'):
                if str(h.relative_to(ROOT)) not in stubs: err('%s: html without stub' % h.name)
    # html files and tested flag
    try: tr = json.loads((ROOT / 'tools/visuals/test-results.json').read_text())
    except Exception: tr = {}
    for d in domains:
        hd = ROOT / 'Visuals' / d / 'html'
        for h in (sorted(hd.glob('*.html')) if hd.exists() else []):
            t = h.read_text(); nm = h.name
            if re.search(r'(src|href)=["\']https?:|url\(\s*["\']?https?:|<script[^>]+src=', t, re.I): err('%s: external reference' % nm)
            body = re.sub(r'<script.*?</script>', '', t, flags=re.S)
            if re.search(r'\bfetch\s*\(|XMLHttpRequest', t) or re.search(r'[^.\w]import\s*\(', t): err('%s: forbidden API' % nm)
            if len(t.encode()) > 400 * 1024: err('%s: over 400 KB' % nm)
            if not re.search(r'<title>[^<]+</title>', t) or 'lang="en-GB"' not in t or 'name="viewport"' not in t: err('%s: title, lang or viewport' % nm)
            if "Educational aid; verify against current standards and the manufacturer's rules." not in t: err('%s: notice missing' % nm)
            if not re.search(r'<h1[ >]', body) or '<main' not in body: err('%s: static h1/main missing' % nm)
            if 'scroll-behavior' not in t or 'prefers-reduced-motion' not in t: err('%s: css scroll/motion' % nm)
            src = ROOT / 'tools/visuals/src' / d / (nm[:-5] + '.jsx')
            if not src.exists(): err('%s: no JSX source' % nm)
    for n, fm in notes.items():
        if fm.get('type') == 'visual' and fm.get('tested') is True:
            key = str(fm.get('file', '')).split('/')[-1][:-5]
            e = tr.get(key)
            if not (e and e.get('pass') and e.get('tests', 0) > 0): err('%s: tested true without a passing test entry' % n)
    lessons = {fm.get('section'): n for n, fm in notes.items() if fm.get('type') == 'visual' and fm.get('kind') == 'lesson'}
    missing = [s for s in sections if s not in lessons]
    if missing: rep('sections with no lesson: %d (%s)' % (len(missing), ', '.join(missing[:3])))
    for sec, n in lessons.items():
        for ix, fmi in notes.items():
            if fmi.get('type') == 'kb' and fmi.get('kind') == 'index' and fmi.get('section') == sec:
                if re.sub(r'[\[\]"]', '', str(fmi.get('companion', ''))) != n: err('%s: index companion is not the lesson' % ix)
                if re.sub(r'[\[\]"]', '', str(notes[n].get('companion', ''))) != ix: err('%s: lesson companion is not the index' % n)
    for t, uses in sorted(tag_uses.items()):
        if len(uses) <= 2: warn('tag %s is used on only %d note%s (%s)' % (t, len(uses), '' if len(uses) == 1 else 's', ', '.join(uses)))
    # reports
    orphans = [n for n, c in incoming.items() if c == 0]
    if orphans: rep('orphans (no incoming links): %d e.g. %s' % (len(orphans), ', '.join(orphans[:4])))
    short = [n for n, fm in notes.items() if fm.get('type') == 'kb' and fm.get('kind') not in ('index', 'glossary', 'checklist', 'faq') and word_counts[n] < 250]
    if short: rep('kb notes under 250 words: %d e.g. %s' % (len(short), ', '.join(short[:4])))
    tested = set()
    for n, fm in notes.items():
        if fm.get('type') in ('exercise', 'scenario'):
            for t in fm.get('tests') or []: tested.add(re.sub(r'[\[\]"]', '', str(t)))
    untested = [n for n, fm in notes.items() if fm.get('type') == 'kb' and fm.get('kind') == 'concept' and n not in tested]
    rep('concept notes with no exercise or scenario: %d' % len(untested))
    novis = [n for n, fm in notes.items() if fm.get('type') == 'kb' and fm.get('kind') == 'concept' and not fm.get('companion')]
    rep('concept notes with no companion visual: %d' % len(novis))
    from collections import Counter
    c = Counter(fm.get('type') for fm in notes.values())
    rep('notes: ' + ', '.join('%s %d' % kv for kv in sorted(c.items())))
    for cand in sorted((ROOT / '_meta/domains').glob('*/CANDIDATES.md')):
        rep('open candidates (%s): %d' % (cand.parent.name, len([l for l in cand.read_text().splitlines() if ' | ' in l and not l.startswith('Format') and not l.rstrip().endswith('| written') and not l.rstrip().endswith('| dropped')])))
    return notes


def check_value(rel, k, val, a, tags, tracks, types, allnames, f2t, names, parsed):
    t = a.get('type')
    def islink(x):
        return isinstance(x, str) and re.fullmatch(r'\[\[[^\[\]]+\]\]', x)
    def link_ok(x):
        if not islink(x): err('%s: %s must be a wiki-link' % (rel, k)); return
        n = WL.findall(x)[0].strip()
        if n not in allnames:
            if n in PLANNED and not STRICT: PENDING[0] += 1
            else: err('%s: %s links to missing %s' % (rel, k, n))
            return
        tg = a.get('target')
        if tg:
            tr = names[n].split('/')[0]
            if f2t.get(tr) != tg: err('%s: %s must link to a %s note (%s)' % (rel, k, tg, n))
    if t == 'enum':
        vals = a.get('values')
        if k == 'type': vals = list(types)
        if vals is not None and val not in vals: err('%s: %s=%r not allowed' % (rel, k, val))
    elif t == 'integer':
        if not isinstance(val, int) or isinstance(val, bool): err('%s: %s must be integer' % (rel, k))
        else:
            if 'min' in a and val < a['min']: err('%s: %s below min' % (rel, k))
            if 'max' in a and val > a['max']: err('%s: %s above max' % (rel, k))
    elif t == 'boolean':
        if not isinstance(val, bool): err('%s: %s must be boolean' % (rel, k))
    elif t == 'string':
        if not isinstance(val, str): err('%s: %s must be string' % (rel, k))
        elif a.get('pattern') and not re.search(a['pattern'], val): err('%s: %s pattern' % (rel, k))
    elif t == 'datetime':
        if not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d', str(val)): err('%s: %s datetime format' % (rel, k))
    elif t == 'date':
        if not re.fullmatch(r'\d{4}-\d\d-\d\d', str(val)): err('%s: %s date format' % (rel, k))
    elif t == 'link':
        link_ok(val)
    elif t == 'list':
        if not isinstance(val, list): err('%s: %s must be a list' % (rel, k)); return
        it = a.get('items')
        for x in val:
            if it == 'link': link_ok(x)
            elif it == 'term':
                voc = tags if a['vocabulary'] == 'tags' else tracks
                if x not in voc: err('%s: %s term %r not preferred' % (rel, k, x))
            elif it == 'string' and not isinstance(x, str): err('%s: %s item must be string' % (rel, k))


def show_domain(S, slug):
    """Print every override a domain has and the effective property list per type."""
    dom, types, full = S['dom'], S['types'], S['full']
    if slug not in dom['domains']:
        print('unknown domain %s (domains: %s)' % (slug, ', '.join(dom['domains']))); return 2
    b = dom['found'].get(slug) or {'types': {}, 'modules': {}, 'vocs': {}}
    print('domain: %s' % slug)
    print('overrides:')
    if not (b['types'] or b['modules'] or b['vocs']): print('  none: the default schema applies')
    for kind in ('modules', 'types'):
        for name, (rel, d) in sorted(b[kind].items()):
            print('  %s' % rel)
            for prop, ch in (d.get('override') or {}).items():
                print('    override %s: %s' % (prop, '; '.join('%s %s' % (k, v) for k, v in ch.items())))
            for prop, nd in (d.get('add') or {}).items():
                print('    add %s: %s' % (prop, ', '.join('%s %s' % (k, v) for k, v in nd.items())))
            for prop in d.get('remove') or []: print('    remove %s' % prop)
            if d.get('sections'): print('    sections: %s' % ', '.join(d['sections']))
    for name, (rel, d, good) in sorted(b['vocs'].items()):
        print('  %s' % rel)
        print('    terms: %s' % ', '.join(d['terms']))
    print('effective properties:')
    for tn in types:
        props = dom['eff'].get((slug, tn), full[tn])
        keys = list(props)
        shown = [k for k in keys if k not in ('created', 'modified')] + [k for k in ('created', 'modified') if k in keys]   # as written in a note
        print('  %s: %s' % (tn, ', '.join(shown)))
        added = [k for k in keys if k not in full[tn]]
        removed = [k for k in full[tn] if k not in props]
        changed = [k for k in keys if k in full[tn] and props[k] != full[tn][k]]
        if added: print('    added: %s' % ', '.join(added))
        if removed: print('    removed: %s' % ', '.join(removed))
        for k in changed:
            diff = ['%s %s' % (a, props[k].get(a)) for a in sorted(set(props[k]) | set(full[tn][k])) if props[k].get(a) != full[tn][k].get(a)]
            print('    changed %s: %s' % (k, '; '.join(diff)))
    for vn in S['vocs']:
        eff = dom['effvoc'].get((slug, vn))
        if eff is not None:
            extra = [t for t in eff if t not in S['vocs'][vn]['terms']]
            print('  vocabulary %s: default %d terms + %d for this domain (%s)' % (vn, len(S['vocs'][vn]['terms']), len(extra), ', '.join(extra)))
    return 1 if ERRORS else 0


def main():
    try:
        sys.path.insert(0, str(ROOT / 'tools')); import mknote
        PLANNED.update(i['name'] for i in mknote.plan()[0])
    except Exception as e:
        pass
    S = check_schema()
    if _opt('--domain') is not None:
        code = show_domain(S, _opt('--domain')) if S else 1
        for e in ERRORS: print('ERROR ' + e)
        sys.exit(code)
    if S: check_notes(S)
    limit = None if '--all' in sys.argv else 60
    for e in ERRORS[:limit]: print('ERROR ' + e)
    if limit and len(ERRORS) > limit: print('... %d more errors (use --all)' % (len(ERRORS) - limit))
    if '--reports' in sys.argv or not ERRORS:
        for r in REPORTS: print('report: ' + r)
    if '--warnings' in sys.argv:
        for w in WARNINGS: print('warning: ' + w)
    print('%d errors; %d links to planned notes not yet written' % (len(ERRORS), PENDING[0]))
    sys.exit(1 if ERRORS else 0)


if __name__ == '__main__':
    main()
