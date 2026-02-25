interface FooterProps {
  t: { made_with: string; rights: string };
}

export default function Footer({ t }: FooterProps) {
  return (
    <footer className="border-t border-gray-100 bg-white py-8">
      <div className="mx-auto max-w-6xl px-4 text-center text-sm text-gray-500">
        <p>
          {t.made_with}{" "}
          <span className="font-semibold text-brand-dark">One-Click Report AI</span>{" "}
          &mdash; {new Date().getFullYear()} {t.rights}
        </p>
      </div>
    </footer>
  );
}
