import React from 'react';

const HeroSection: React.FC = () => (
  <section className="flex flex-col items-center justify-center pt-8 pb-6 md:pt-12 md:pb-8">
    <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-8 mb-6 md:mb-8 w-full">
      {/* Left image */}
      <img
        src="https://i.imgur.com/4QfKuz1.png"
        alt="Coco Pops"
        className="w-32 h-32 md:w-48 md:h-48 object-contain -rotate-12 md:-rotate-15 mb-2 md:mb-0"
        style={{ transform: 'rotate(-12deg)' }}
      />
      {/* Headline */}
      <h1 className="text-2xl sm:text-3xl md:text-5xl font-bold text-center max-w-xs sm:max-w-md md:max-w-2xl">
        Discover best quality<br />food products that fit<br />your palette
      </h1>
      {/* Right image */}
      <img
        src="https://i.imgur.com/4QfKuz1.png"
        alt="Ginger Beer"
        className="w-28 h-32 md:w-40 md:h-48 object-contain rotate-12 md:rotate-15 mt-2 md:mt-0"
        style={{ transform: 'rotate(12deg)' }}
      />
    </div>
  </section>
);

export default HeroSection; 