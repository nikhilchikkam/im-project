type ProductTagsSectionProps = {
  title: string;
  tags: string[];
};

const ProductTagsSection = ({ title, tags }: ProductTagsSectionProps) => (
  <div className="bg-white border rounded-lg p-3 flex-1 min-w-[180px]">
    <div className="text-xs font-semibold text-gray-700 mb-2">{title}</div>
    <div className="flex gap-2 flex-wrap">
      {tags.map((tag, i) => (
        <span key={i} className="bg-blue-100 text-blue-700 rounded-full px-3 py-1 text-xs font-medium">
          {tag}
        </span>
      ))}
    </div>
  </div>
);

export default ProductTagsSection; 