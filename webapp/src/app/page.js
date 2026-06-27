import ImageUploader from '@/components/ImageUploader';

export const metadata = {
  title: 'Oxalate Analyzer',
  description: 'Analyze food images for oxalate content',
};

export default function Home() {
  return (
    <main className="container">
      <header style={{ textAlign: 'center', marginBottom: '3rem', marginTop: '2rem' }}>
        <h1 className="text-gradient" style={{ fontSize: '3rem', marginBottom: '1rem' }}>
          Oxalate Analyzer
        </h1>
        <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '1.2rem' }}>
          Upload a photo of your meal or ingredients to instantly analyze its oxalate content.
        </p>
      </header>
      
      <section className="animate-fade-in" style={{ animationDelay: '0.2s' }}>
        <ImageUploader />
      </section>
    </main>
  );
}
