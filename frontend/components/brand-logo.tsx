import Image from "next/image";

type BrandLogoProps = {
  compact?: boolean;
  showTagline?: boolean;
  tagline?: string;
};

export function BrandLogo({ compact = false, showTagline = true, tagline }: BrandLogoProps) {
  return (
    <div className={`brand-row${compact ? " compact" : ""}`}>
      <Image
        src="/matious-logo.png"
        alt="MatiousHire logo"
        width={compact ? 140 : 180}
        height={compact ? 36 : 48}
        className="brand-logo"
        priority
      />
      {showTagline && (
        <div>
          <strong>MatiousHire</strong>
          {tagline && <span>{tagline}</span>}
        </div>
      )}
    </div>
  );
}
