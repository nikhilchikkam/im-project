import React from 'react';
import Toolbar from '../../components/ui/Toolbar';

type WishlistToolbarProps = {
  title: string;
  onBack: () => void;
  onTitleChange: (newTitle: string) => void;
  onShare: () => void;
  onAddItem: () => void;
};

const WishlistToolbar: React.FC<WishlistToolbarProps> = ({ title, onBack, onTitleChange, onShare, onAddItem }) => {
  return (
    <Toolbar
      title={title}
      onBack={onBack}
      onTitleChange={onTitleChange}
      onShare={onShare}
      onAddItem={onAddItem}
      showShare={true}
      showAddItem={true}
      addItemLabel="+ Add item"
    />
  );
};

export default WishlistToolbar; 