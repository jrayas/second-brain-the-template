import { useState, useEffect } from 'preact/hooks';

export const NOTICE = "Educational aid; verify against current standards and the manufacturer's rules.";

export function Layout({ meta, toc = [], children }) {
  const [active, setActive] = useState(toc[0] ? toc[0].id : '');
  const [pct, setPct] = useState(0);
  useEffect(() => {
    if (typeof IntersectionObserver === 'undefined') return;
    const obs = new IntersectionObserver((es) => {
      for (const e of es) if (e.isIntersecting) setActive(e.target.id);
    }, { rootMargin: '0px 0px -70% 0px' });
    toc.forEach((t) => { const el = document.getElementById(t.id); if (el) obs.observe(el); });
    const onScroll = () => {
      const h = document.documentElement.scrollHeight - window.innerHeight;
      setPct(h > 0 ? Math.min(100, (window.scrollY / h) * 100) : 0);
    };
    const onPrint = () => document.querySelectorAll('details').forEach((d) => d.setAttribute('open', ''));
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('beforeprint', onPrint);
    return () => { obs.disconnect(); window.removeEventListener('scroll', onScroll); window.removeEventListener('beforeprint', onPrint); };
  }, []);
  return (
    <>
      <a class="skip" href="#main">Skip to the content</a>
      <div class="progress" aria-hidden="true"><div style={{ width: pct + '%' }}></div></div>
      <header class="top"><div class="wrap">
        <strong>{meta.brand || 'Knowledge base'}</strong>
        <span><span class="badge">{meta.kind || 'Interactive page'}</span> <span class="badge">{meta.level}</span> <span class="badge">about {meta.minutes} min</span></span>
      </div></header>
      <div class="wrap layout">
        <main id="main" class="readcol">
          <h1>{meta.title}</h1>
          <p class="lead">{meta.lead}</p>
          {meta.learn && (<div class="card"><strong>What you will learn</strong><ul>{meta.learn.map((x) => <li>{x}</li>)}</ul></div>)}
          {children}
          <p class="notice">{NOTICE} Companion note: <strong>{meta.companion}</strong>. Every number on this page comes from that note or the notes it links.</p>
        </main>
        {toc.length > 0 && (
          <aside class="toc"><nav aria-label="Contents"><strong>Contents</strong>
            <ol>{toc.map((t) => <li><a href={'#' + t.id} aria-current={active === t.id ? 'true' : 'false'}>{t.title}</a></li>)}</ol>
          </nav></aside>
        )}
      </div>
    </>
  );
}

export function Section({ id, title, children }) {
  return <section id={id} aria-labelledby={id + '-h'}><h2 id={id + '-h'}>{title}</h2>{children}</section>;
}

export function Callout({ kind = 'info', title, children }) {
  return <div class={'callout ' + kind}>{title && <strong class="t">{title}</strong>}{children}</div>;
}
export function Mistake({ children }) { return <div class="callout bad mistake">{children}</div>; }

export function Reveal({ summary, children }) {
  return <details><summary>{summary}</summary><div style="padding-bottom:.6rem">{children}</div></details>;
}

export function Figure({ title, desc, viewBox = '0 0 640 300', caption, children }) {
  const k = title.toLowerCase().replace(/\W+/g, '-');
  return (
    <figure class="fig">
      <svg viewBox={viewBox} role="img" aria-labelledby={k + '-t ' + k + '-d'}><title id={k + '-t'}>{title}</title><desc id={k + '-d'}>{desc}</desc>{children}</svg>
      {caption && <figcaption><strong>What to notice:</strong> {caption}</figcaption>}
    </figure>
  );
}

export function Slider({ label, unit = '', min, max, step = 1, value, onInput, fmt }) {
  const id = 'sl-' + label.replace(/\W+/g, '-');
  const shown = fmt ? fmt(value) : String(value);
  return (
    <div class="slider">
      <label for={id}>{label}</label>
      <output for={id} aria-live="polite">{shown} {unit}</output>
      <input id={id} type="range" min={min} max={max} step={step} value={value}
        onInput={(e) => onInput(Number(e.currentTarget.value))} />
    </div>
  );
}

export function QuickCheck({ q, options, id }) {
  const [pick, setPick] = useState(-1);
  const correct = options.findIndex((o) => o.ok);
  return (
    <div class="card" id={id}>
      <strong>Quick check.</strong> {q}
      <div class="opts" role="group" aria-label="Choices">
        {options.map((o, i) => (
          <button type="button" aria-pressed={pick === i ? 'true' : 'false'} class={pick === i ? (o.ok ? 'right' : 'wrong') : ''} onClick={() => setPick(i)}>{o.t}</button>
        ))}
      </div>
      <div aria-live="polite">{pick >= 0 && (<Callout kind={options[pick].ok ? 'good' : 'bad'} title={options[pick].ok ? 'Correct' : 'Not quite'}>{options[pick].why}</Callout>)}</div>
      <details><summary>Show the answer and why each choice is right or wrong</summary>
        <p><strong>Answer:</strong> {options[correct].t}</p>
        <ul>{options.map((o) => <li><strong>{o.t}</strong>: {o.why}</li>)}</ul>
      </details>
    </div>
  );
}

export function Steps({ steps, label = 'Step through' }) {
  const [i, setI] = useState(0);
  return (
    <div class="card">
      <strong>{label}</strong>
      <div aria-live="polite"><p><strong>Step {i + 1} of {steps.length}: {steps[i].title}</strong></p>{steps[i].body}</div>
      <button type="button" onClick={() => setI(Math.max(0, i - 1))} disabled={i === 0}>Back</button>{' '}
      <button type="button" class="primary" onClick={() => setI(Math.min(steps.length - 1, i + 1))} disabled={i === steps.length - 1}>Next</button>{' '}
      <button type="button" onClick={() => setI(0)}>Restart</button>
    </div>
  );
}

export function Tabs({ items, label }) {
  const [i, setI] = useState(0);
  return (
    <div class="card">
      {label && <strong>{label}</strong>}
      <div role="group" aria-label={label || 'Options'} style="display:flex;flex-wrap:wrap;gap:.5rem;margin:.5rem 0">
        {items.map((it, k) => <button type="button" aria-pressed={i === k ? 'true' : 'false'} class={i === k ? 'primary' : ''} onClick={() => setI(k)}>{it.name}</button>)}
      </div>
      <div aria-live="polite">{items[i].body}</div>
    </div>
  );
}

export function Table({ head, rows }) {
  return <div class="tablewrap"><table class="t"><thead><tr>{head.map((h) => <th scope="col">{h}</th>)}</tr></thead>
    <tbody>{rows.map((r) => <tr>{r.map((c) => <td>{c}</td>)}</tr>)}</tbody></table></div>;
}

export function Summary({ items, mistakes = [], next = [], selfTest }) {
  return (
    <>
      <Section id="summary" title="Summary">
        <ul>{items.map((x) => <li>{x}</li>)}</ul>
        {mistakes.length > 0 && (<><h3>Common mistakes</h3><ul>{mistakes.map((x) => <li>{x}</li>)}</ul></>)}
      </Section>
      {selfTest}
      <Section id="next" title="Where next">
        <ul>{next.map((x) => <li><strong>{x}</strong></li>)}</ul>
      </Section>
    </>
  );
}

export function SelfTest({ items }) {
  return (
    <Section id="selftest" title="Self-test">
      <p>Five questions. None is required; the answers explain themselves.</p>
      {items.map((it, k) => <QuickCheck id={'st' + k} q={it.q} options={it.options} />)}
    </Section>
  );
}

export function Flow({ steps, label = 'Flow' }) {
  const [open, setOpen] = useState(0);
  return (
    <ol class="card" aria-label={label} style="list-style:none;padding:.6rem 1rem">
      {steps.map((s, i) => (
        <li style="margin:.2rem 0">
          <button type="button" aria-expanded={open === i ? 'true' : 'false'} class={open === i ? 'primary' : ''} style="width:100%;text-align:left" onClick={() => setOpen(open === i ? -1 : i)}>
            {i + 1}. {s.title}
          </button>
          {open === i && <div style="padding:.5rem .8rem" aria-live="polite">{s.body}{s.check && <p><strong>Check:</strong> {s.check}</p>}</div>}
          {i < steps.length - 1 && <div aria-hidden="true" style="text-align:center;color:var(--muted)">↓</div>}
        </li>
      ))}
    </ol>
  );
}

// Decision tree: nodes = { id: { q, yes, no } | { end: 'text' } }
export function Tree({ nodes, start }) {
  const [path, setPath] = useState([start]);
  const cur = nodes[path[path.length - 1]];
  const answer = (k) => setPath([...path, cur[k]]);
  return (
    <div class="card">
      <ol aria-label="Your answers so far" style="color:var(--muted);font-size:.92rem">
        {path.slice(0, -1).map((id, i) => <li>{nodes[id].q} <strong>{path[i + 1] === nodes[id].yes ? 'Yes' : 'No'}</strong></li>)}
      </ol>
      <div aria-live="polite">
        {cur.end ? <Callout kind="good" title="Likely next step">{cur.end}</Callout> : <p><strong>{cur.q}</strong></p>}
      </div>
      {!cur.end && (<div style="display:flex;gap:.6rem"><button type="button" class="primary" onClick={() => answer('yes')}>Yes</button><button type="button" onClick={() => answer('no')}>No</button></div>)}
      <p><button type="button" onClick={() => setPath([start])}>Start again</button>{path.length > 1 && <> <button type="button" onClick={() => setPath(path.slice(0, -1))}>Back one step</button></>}</p>
    </div>
  );
}

// A lesson: hero, contents, 5 to 9 sections (hook, content, quick check, common mistake), summary, self-test, where next.
export function Lesson({ meta, sections, summary, mistakes = [], selfTest, next }) {
  const toc = [...sections.map((s) => ({ id: s.id, title: s.title })), { id: 'summary', title: 'Summary' }, { id: 'selftest', title: 'Self-test' }, { id: 'next', title: 'Where next' }];
  return (
    <Layout meta={{ ...meta, kind: 'Lesson' }} toc={toc}>
      {sections.map((s) => (
        <Section id={s.id} title={s.title}>
          <p class="lead"><em>{s.hook}</em></p>
          {s.children}
          {s.check && <QuickCheck q={s.check.q} options={s.check.options} />}
          {s.mistake && <Mistake>{s.mistake}</Mistake>}
        </Section>
      ))}
      <Summary items={summary} mistakes={mistakes} next={next} selfTest={<SelfTest items={selfTest} />} />
    </Layout>
  );
}
