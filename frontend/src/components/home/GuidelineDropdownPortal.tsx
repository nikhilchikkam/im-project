import type { ReactNode } from 'react';
import { createPortal } from 'react-dom';

const GuidelineDropdownPortal = ({ children }: { children: ReactNode }) => {
  if (typeof window === 'undefined') return null;
  return createPortal(children, document.body);
};

export default GuidelineDropdownPortal; 