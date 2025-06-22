import React from 'react';
import NavbarAfter from '../components/navigation/NavbarAfter';

type ProfilePageLayoutProps = {
  sidebar: React.ReactNode;
  children: React.ReactNode;
};

const ProfilePageLayout: React.FC<ProfilePageLayoutProps> = ({ sidebar, children }) => {
  return (
    <div className="flex min-h-screen flex-col bg-gray-100">
      <NavbarAfter />
      <div className="container mx-auto flex flex-grow gap-8 px-6 py-8">
        <aside className="w-1/4 flex-shrink-0">
          {sidebar}
        </aside>
        <main className="w-3/4 flex-grow">
          {children}
        </main>
      </div>
    </div>
  );
};

export default ProfilePageLayout; 