import { Archivo, Spline_Sans_Mono } from 'next/font/google';

// Type pairing on a contrast axis (proportional grotesque + monospace),
// per D-011's craft-meets-engineering direction. Archivo is a technical
// grotesque (precise, warm, structural); Spline Sans Mono carries the
// record IDs (D-001 / R-002 / T-003) as real engineering annotations, not
// mono-as-costume. Both chosen off the reflex-default set (Inter / Plex /
// Space families).
export const fontSans = Archivo({
  subsets: ['latin'],
  variable: '--font-archivo',
  display: 'swap',
});

export const fontMono = Spline_Sans_Mono({
  subsets: ['latin'],
  variable: '--font-spline-mono',
  display: 'swap',
});
