import React from 'react';
import Toolbar from '../../components/ui/Toolbar';

type CartToolbarProps = {
  title: string;
  onBack: () => void;
  onTitleChange: (newTitle: string) => void;
  onShare: (action: string) => void;
  onAddItem: () => void;
};

const CartToolbar: React.FC<CartToolbarProps> = ({ title, onBack, onTitleChange, onShare, onAddItem }) => {
  return (
    <Toolbar
      title={title}
      onBack={onBack}
      onTitleChange={onTitleChange}
      onShare={() => onShare("share")}
      onAddItem={onAddItem}
      showShare={true}
      showAddItem={true}
      addItemLabel="+ Add item"
    />
  );
};

export default CartToolbar; 