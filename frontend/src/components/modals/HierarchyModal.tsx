import React, { useState, useEffect } from 'react';
import type { ReactElement } from 'react';
import { Modal } from './Modal';
import HierarchyGraph from './HierarchyGraph';

interface HierarchyModalProps {
  isOpen: boolean;
  onClose: () => void;
  gtin: string;
}

interface HierarchyNode {
  gtin: string;
  name: string;
  normalized_name?: string;
  product_type?: string;
  gpc_code?: string;
  family_title?: string;
  nutrient_available?: boolean;
  allergen_available?: boolean;
}

interface HierarchyRelationship {
  source: string;
  target: string;
  type: string;
}

interface HierarchyData {
  nodes: HierarchyNode[];
  relationships: HierarchyRelationship[];
}

interface ProductData {
  gtin: string;
  name: string;
  normalized_name?: string;
  product_type?: string;
  gpc_code?: string;
  family_title?: string;
  nutrition?: any[];
}

const HierarchyModal: React.FC<HierarchyModalProps> = ({ isOpen, onClose, gtin }) => {
  const [hierarchyData, setHierarchyData] = useState<HierarchyData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'graph' | 'text' | 'table'>('graph');

  useEffect(() => {
    if (isOpen && gtin) {
      fetchHierarchyData();
    }
  }, [isOpen, gtin]);

  const fetchHierarchyData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Step 1: Fetch hierarchy structure from Neo4j API
      const hierarchyResponse = await fetch(`/api/neo4j/hierarchy/${gtin}`);
      
      if (!hierarchyResponse.ok) {
        throw new Error(`HTTP error! status: ${hierarchyResponse.status}`);
      }
      
      const hierarchyResult = await hierarchyResponse.json();
      
      // Step 2: Fetch detailed product information for all nodes
      const enrichedNodes = await Promise.all(
        hierarchyResult.nodes.map(async (node: any) => {
          try {
            // Fetch product details
            const productResponse = await fetch(`/api/products/${node.gtin}`);
            let productData: ProductData | null = null;
            
            if (productResponse.ok) {
              productData = await productResponse.json();
            }
            
            // Fetch allergen information
            const allergenResponse = await fetch(`/api/allergens/${node.gtin}`);
            let allergenData: any[] = [];
            
            if (allergenResponse.ok) {
              allergenData = await allergenResponse.json();
            }
            
            return {
              gtin: node.gtin,
              name: node.name,
              normalized_name: productData?.normalized_name,
              product_type: productData?.product_type,
              gpc_code: productData?.gpc_code,
              family_title: productData?.family_title,
              nutrient_available: productData?.nutrition && productData.nutrition.length > 0,
              allergen_available: allergenData && allergenData.length > 0
            };
          } catch (err) {
            console.error(`Error fetching data for GTIN ${node.gtin}:`, err);
            // Return basic node data if API calls fail
            return {
              gtin: node.gtin,
              name: node.name,
              normalized_name: null,
              product_type: null,
              gpc_code: null,
              family_title: null,
              nutrient_available: false,
              allergen_available: false
            };
          }
        })
      );
      
      setHierarchyData({
        nodes: enrichedNodes,
        relationships: hierarchyResult.relationships
      });
      
    } catch (err) {
      console.error('Error fetching hierarchy data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load hierarchy');
    } finally {
      setLoading(false);
    }
  };

  const renderHierarchyText = () => {
    if (!hierarchyData) return null;

    const { nodes, relationships } = hierarchyData;
    
    // Create a map of nodes for easy lookup
    const nodeMap = new Map(nodes.map(node => [node.gtin, node.normalized_name || node.name]));
    
    // Group relationships by source to show hierarchy structure
    const hierarchyMap = new Map<string, string[]>();
    
    relationships.forEach(rel => {
      if (!hierarchyMap.has(rel.source)) {
        hierarchyMap.set(rel.source, []);
      }
      hierarchyMap.get(rel.source)!.push(rel.target);
    });

    const renderNode = (gtin: string, level: number = 0): ReactElement => {
      const name = nodeMap.get(gtin) || 'Unknown';
      const children = hierarchyMap.get(gtin) || [];
      const indent = '  '.repeat(level);
      
      return (
        <div key={gtin} className="mb-2">
          <div className="font-medium">
            {indent}• {name} (GTIN: {gtin})
          </div>
          {children.map(childGtin => renderNode(childGtin, level + 1))}
        </div>
      );
    };

    // Find root nodes (nodes that are not targets of any relationship)
    const targetGtins = new Set(relationships.map(rel => rel.target));
    const rootGtins = nodes
      .map(node => node.gtin)
      .filter(gtin => !targetGtins.has(gtin));

    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Product Hierarchy</h3>
        <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
          {rootGtins.length > 0 ? (
            rootGtins.map(gtin => renderNode(gtin))
          ) : (
            <div className="text-gray-500">No hierarchy data available</div>
          )}
        </div>
        
        <div className="text-sm text-gray-600">
          <p>Total nodes: {nodes.length}</p>
          <p>Total relationships: {relationships.length}</p>
        </div>
      </div>
    );
  };

  const renderGraphView = () => {
    if (!hierarchyData) return null;

    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Graph Visualization</h3>
        <div className="flex justify-center">
          <HierarchyGraph 
            data={hierarchyData} 
            width={1000} 
            height={700} 
          />
        </div>
        <div className="text-sm text-gray-600 text-center">
          <p>Click on nodes to highlight connections • Hover for detailed information</p>
          <p>Total nodes: {hierarchyData.nodes.length}</p>
          <p>Total relationships: {hierarchyData.relationships.length}</p>
        </div>
      </div>
    );
  };

  const renderTableView = () => {
    if (!hierarchyData) return null;

    const { nodes, relationships } = hierarchyData;
    
    // Create a map of relationships for easy lookup
    const relationshipMap = new Map<string, string[]>();
    relationships.forEach(rel => {
      if (!relationshipMap.has(rel.source)) {
        relationshipMap.set(rel.source, []);
      }
      relationshipMap.get(rel.source)!.push(rel.target);
    });

    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Product Details Table</h3>
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Product Information
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Classification
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Data Availability
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Hierarchy
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {nodes.map((node, index) => (
                  <tr key={node.gtin} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {node.normalized_name || node.name}
                        </div>
                        <div className="text-sm text-gray-500">
                          GTIN: {node.gtin}
                        </div>
                        {node.name !== node.normalized_name && node.name && (
                          <div className="text-xs text-gray-400">
                            Original: {node.name}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {node.product_type && (
                          <div>Type: {node.product_type}</div>
                        )}
                        {node.gpc_code && (
                          <div>GPC: {node.gpc_code}</div>
                        )}
                        {node.family_title && (
                          <div>Family: {node.family_title}</div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex space-x-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          node.nutrient_available 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {node.nutrient_available ? '✓' : '✗'} Nutrition
                        </span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          node.allergen_available 
                            ? 'bg-yellow-100 text-yellow-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {node.allergen_available ? '✓' : '✗'} Allergen
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div>
                        {relationshipMap.has(node.gtin) ? (
                          <div>
                            <div>Children: {relationshipMap.get(node.gtin)?.length || 0}</div>
                            <div className="text-xs text-gray-400">
                              {relationshipMap.get(node.gtin)?.slice(0, 2).join(', ')}
                              {relationshipMap.get(node.gtin) && relationshipMap.get(node.gtin)!.length > 2 && '...'}
                            </div>
                          </div>
                        ) : (
                          <span className="text-gray-400">Leaf node</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        
        <div className="text-sm text-gray-600">
          <p>Total nodes: {nodes.length}</p>
          <p>Total relationships: {relationships.length}</p>
        </div>
      </div>
    );
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Product Hierarchy" maxWidth="7xl">
      <div className="p-6">
        {/* View Mode Toggle */}
        <div className="flex justify-center mb-6">
          <div className="bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('graph')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'graph'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Graph View
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'table'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Table View
            </button>
            <button
              onClick={() => setViewMode('text')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'text'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Text View
            </button>
          </div>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2">Loading hierarchy...</span>
          </div>
        )}
        
        {error && (
          <div className="text-center py-8">
            <div className="text-red-600 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-red-600 mb-2">Failed to load hierarchy</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={fetchHierarchyData}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        )}
        
        {!loading && !error && hierarchyData && (
          viewMode === 'graph' ? renderGraphView() : 
          viewMode === 'table' ? renderTableView() : 
          renderHierarchyText()
        )}
      </div>
    </Modal>
  );
};

export default HierarchyModal; 