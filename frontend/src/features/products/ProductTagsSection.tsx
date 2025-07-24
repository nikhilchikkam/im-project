type ProductTagsSectionProps = {
  title: string;
  tags: string[];
  emptyText?: string;
};

const ProductTagsSection = ({ title, tags, emptyText }: ProductTagsSectionProps) => (
  <div className="bg-white border rounded-lg p-3 flex-1 min-w-[180px]">
    <div className="text-xs font-semibold text-gray-700 mb-2">{title}</div>
    <div className="flex gap-2 flex-wrap">
      {tags.length > 0 ? (
        tags.map((tag, i) => (
          <span key={i} className="bg-blue-100 text-blue-700 rounded-full px-3 py-1 text-xs font-medium">
            {tag}
          </span>
        ))
      ) : (
        <span className="text-xs text-gray-400">{emptyText || 'No data available'}</span>
      )}
    </div>
  </div>
);

export default ProductTagsSection; 