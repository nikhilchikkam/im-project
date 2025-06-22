import React, { useState, cloneElement, isValidElement } from 'react';
import { Pencil } from 'lucide-react';

type InfoCardProps = {
  title: string;
  onSave: (data: any) => void;
  children: React.ReactNode;
};

const InfoCard: React.FC<InfoCardProps> = ({ title, onSave, children }) => {
  const [isEditing, setIsEditing] = useState(false);

  const handleToggleEdit = () => {
    if (isEditing) {
      onSave({}); // In a real app, collect form data here
    }
    setIsEditing(!isEditing);
  };
  
  const renderChildrenWithProps = (nodes: React.ReactNode): React.ReactNode => {
    return React.Children.map(nodes, child => {
      if (!isValidElement(child)) {
        return child;
      }
      
      const props = (child as any).props;
      const childProps: { [key: string]: any } = { ...props };

      // Check if the component is one of our local InputFields by checking its name,
      // or if it's a standard HTML input element. This is more robust.
      const isDisableable = 
        (typeof child.type === 'function' && (child.type as any).name === 'InputField') ||
        (typeof child.type === 'string' && ['input', 'textarea', 'select'].includes(child.type));

      if (isDisableable) {
        childProps.disabled = !isEditing;
      }
      
      if (props.children) {
        childProps.children = renderChildrenWithProps(props.children);
      }
      
      return cloneElement(child, childProps);
    });
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-sm mb-8">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-semibold text-gray-800">{title}</h3>
        <button
          onClick={handleToggleEdit}
          className="bg-gray-100 text-gray-600 font-semibold px-6 py-2 rounded-lg hover:bg-gray-200 transition text-sm flex items-center gap-2"
        >
          <Pencil className="w-3 h-3" />
          <span>{isEditing ? 'Save' : 'Edit'}</span>
        </button>
      </div>
      <div>{renderChildrenWithProps(children)}</div>
    </div>
  );
};

export default InfoCard; 