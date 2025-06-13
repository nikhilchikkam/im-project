const ResourcesPage = () => {
  return (
    <div className="max-w-6xl mx-auto px-4 py-16">
      <h1 className="text-3xl font-bold mb-4">Resources</h1>
      <p className="text-gray-600 mb-8">
        Find documentation, regulatory links, and industry standards for food classification, labeling, and analysis.
      </p>
      <ul className="list-disc list-inside space-y-2">
        <li>USDA FoodData Central</li>
        <li>FDA Nutrition Guidelines</li>
        <li>GPC Product Classification</li>
        <li>Supplier Collaboration Tips</li>
      </ul>
    </div>
  );
};

export default ResourcesPage;
