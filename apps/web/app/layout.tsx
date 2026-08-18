import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = { title: 'BIM Control X', description: 'BIM 4D/5D engineering harness' };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="es"><body>{children}</body></html>;
}
