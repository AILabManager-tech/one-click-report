interface HeroProps {
  t: { title: string; subtitle: string; cta: string; cta_demo: string };
}

export default function Hero({ t }: HeroProps) {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-brand-navy via-brand-dark to-brand-purple py-20 md:py-32">
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PHBhdGggZD0iTTM2IDE4YzAtOS45NC04LjA2LTE4LTE4LTE4UzAgOC4wNiAwIDE4czguMDYgMTggMTggMTggMTgtOC4wNiAxOC0xOCIvPjwvZz48L2c+PC9zdmc+')] opacity-40" />

      <div className="relative mx-auto max-w-4xl px-4 text-center">
        <h1 className="mb-6 text-4xl font-extrabold leading-tight text-white md:text-6xl">
          {t.title}
        </h1>
        <p className="mx-auto mb-10 max-w-2xl text-lg text-gray-300 md:text-xl">
          {t.subtitle}
        </p>
        <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <a href="#generate" className="btn-accent text-base px-8 py-4">
            {t.cta}
          </a>
          <a href="#features" className="rounded-xl border-2 border-white/20 px-8 py-4 text-base font-semibold text-white transition-colors hover:border-white/40 hover:bg-white/5">
            {t.cta_demo}
          </a>
        </div>
      </div>
    </section>
  );
}
