// app/layout.tsx
import './globals.css';

export const metadata = {
  title: 'Energy Prices',
  description: 'Oil Prices Dashboard',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      {/* We move the classes from your old <body> here. 
          Next.js handles the Dark Mode toggle via the 'dark' class on <html> 
      */}
      <body className="bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-200 p-4 font-sans transition-colors duration-300">
        <div className="max-w-lg mx-auto">
          {children}
        </div>
      </body>
    </html>
  );
}