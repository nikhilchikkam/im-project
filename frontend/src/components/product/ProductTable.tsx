type Product = {
  id: string;
  category: string;
  itemNumber: string;
  name: string;
  description: string;
};

const ProductTable = ({ products }: { products: Product[] }) => {
  return (
    <div className="w-full bg-white rounded-lg border overflow-x-auto">
      <table className="min-w-full text-left">
        <thead>
          <tr className="border-b text-gray-500 text-sm">
            <th className="px-4 py-2"><input type="checkbox" /></th>
            <th className="px-4 py-2">Category</th>
            <th className="px-4 py-2">Item Number</th>
            <th className="px-4 py-2">Product</th>
            <th className="px-4 py-2">Description</th>
            <th className="px-4 py-2"></th>
          </tr>
        </thead>
        <tbody>
          {products.map((p) => (
            <tr key={p.id} className="border-b hover:bg-gray-50">
              <td className="px-4 py-2"><input type="checkbox" /></td>
              <td className="px-4 py-2"><span className="inline-block bg-red-100 text-red-600 text-xs font-semibold rounded px-2 py-1">• {p.category}</span></td>
              <td className="px-4 py-2">{p.itemNumber}</td>
              <td className="px-4 py-2">{p.name}</td>
              <td className="px-4 py-2">{p.description}</td>
              <td className="px-4 py-2 text-right"><span className="inline-block w-6 h-6 text-gray-400 cursor-pointer">&#8942;</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ProductTable; 