import React from 'react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  pageSize: number;
  onPageSizeChange: (size: number) => void;
  pageSizeOptions?: number[];
}

const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  pageSize,
  onPageSizeChange,
  pageSizeOptions = [12, 24, 36],
}) => {
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];

    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      const left = Math.max(2, currentPage - 2);
      const right = Math.min(totalPages - 1, currentPage + 2);

      pages.push(1);
      if (left > 2) pages.push('left-ellipsis');
      for (let i = left; i <= right; i++) pages.push(i);
      if (right < totalPages - 1) pages.push('right-ellipsis');
      pages.push(totalPages);
    }

    return pages;
  };

  return (
    <div className="w-full flex flex-col items-center gap-2 mt-8">
      <div className="flex items-center gap-1 justify-center">
        <button
          className="px-2 py-1 rounded disabled:text-gray-300"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          &lt; Previous
        </button>
        {getPageNumbers().map((p) =>
          typeof p === 'string' && p.includes('ellipsis') ? (
            <span key={p} className="px-2">...</span>
          ) : (
            <button
              key={p}
              className={`px-3 py-1 rounded ${
                currentPage === p
                  ? 'bg-gray-100 border border-gray-400 text-black font-semibold'
                  : 'hover:bg-gray-100'
              }`}
              onClick={() => onPageChange(p as number)}
              disabled={currentPage === p}
            >
              {p}
            </button>
          )
        )}
        <button
          className="px-2 py-1 rounded disabled:text-gray-300"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          Next &gt;
        </button>
      </div>
      <div className="flex items-center gap-2 justify-center mt-2">
        <span>Products per Page</span>
        <select
          className="border rounded px-2 py-1"
          value={pageSize}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
        >
          {pageSizeOptions.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default Pagination;
