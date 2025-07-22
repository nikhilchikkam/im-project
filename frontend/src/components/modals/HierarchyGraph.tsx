import React, { useEffect, useRef, useState } from 'react';

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

interface GraphNode {
  id: string;
  gtin: string;
  name: string;
  normalized_name?: string;
  product_type?: string;
  gpc_code?: string;
  family_title?: string;
  nutrient_available?: boolean;
  allergen_available?: boolean;
  x: number;
  y: number;
  level: number;
}

interface GraphLink {
  source: string;
  target: string;
  type: string;
}

interface HierarchyGraphProps {
  data: HierarchyData;
  width: number;
  height: number;
}

const HierarchyGraph: React.FC<HierarchyGraphProps> = ({ data, width, height }) => {
  // Defensive checks for data, nodes, and relationships
  if (!data || !Array.isArray(data.nodes) || data.nodes.length === 0) {
    return <div className="text-center text-gray-500 py-8">No hierarchy data available for this product.</div>;
  }
  if (!Array.isArray(data.relationships)) {
    return <div className="text-center text-gray-500 py-8">No relationship data available for this product.</div>;
  }

  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [graphNodes, setGraphNodes] = useState<GraphNode[]>([]);
  const [graphLinks, setGraphLinks] = useState<GraphLink[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [tooltip, setTooltip] = useState<{ show: boolean; content: string; x: number; y: number }>({
    show: false,
    content: '',
    x: 0,
    y: 0
  });

  useEffect(() => {
    if (!data || !svgRef.current) return;

    // Process data to create graph structure
    const { nodes, relationships } = data;
    
    // Create node map
    const nodeMap = new Map(nodes.map(node => [node.gtin, node]));
    
    // Build hierarchy levels
    const levels = new Map<string, number>();
    const children = new Map<string, string[]>();
    
    // Initialize children map
    relationships.forEach(rel => {
      if (!children.has(rel.source)) {
        children.set(rel.source, []);
      }
      children.get(rel.source)!.push(rel.target);
    });
    
    // Calculate levels using BFS
    const visited = new Set<string>();
    const queue: { gtin: string; level: number }[] = [];
    
    // Find root nodes (nodes that are not targets)
    const targetGtins = new Set(relationships.map(rel => rel.target));
    const rootGtins = nodes
      .map(node => node.gtin)
      .filter(gtin => !targetGtins.has(gtin));
    
    rootGtins.forEach(gtin => {
      queue.push({ gtin, level: 0 });
      visited.add(gtin);
    });
    
    while (queue.length > 0) {
      const { gtin, level } = queue.shift()!;
      levels.set(gtin, level);
      
      const childGtins = children.get(gtin) || [];
      childGtins.forEach(childGtin => {
        if (!visited.has(childGtin)) {
          queue.push({ gtin: childGtin, level: level + 1 });
          visited.add(childGtin);
        }
      });
    }
    
    // Calculate max levels and nodes per level
    const maxLevel = Math.max(...levels.values(), 0);
    const nodesPerLevel = new Map<number, string[]>();
    
    nodes.forEach(node => {
      const level = levels.get(node.gtin) || 0;
      if (!nodesPerLevel.has(level)) {
        nodesPerLevel.set(level, []);
      }
      nodesPerLevel.get(level)!.push(node.gtin);
    });
    
    // Create graph nodes with positions
    const graphNodes: GraphNode[] = nodes.map(node => {
      const level = levels.get(node.gtin) || 0;
      const levelNodes = nodesPerLevel.get(level) || [];
      const nodeIndex = levelNodes.indexOf(node.gtin);
      
      // Calculate positions with proper spacing
      const levelWidth = Math.max(levelNodes.length, 1);
      const x = (width * 0.8 / levelWidth) * (nodeIndex + 1) + width * 0.1;
      const y = (height * 0.8 / (maxLevel + 1)) * (level + 1) + height * 0.1;
      
      return {
        id: node.gtin,
        gtin: node.gtin,
        name: node.name,
        normalized_name: node.normalized_name,
        product_type: node.product_type,
        gpc_code: node.gpc_code,
        family_title: node.family_title,
        nutrient_available: node.nutrient_available,
        allergen_available: node.allergen_available,
        x,
        y,
        level
      };
    });
    
    setGraphNodes(graphNodes);
    setGraphLinks(relationships);
    
    // Center the graph initially
    if (graphNodes.length > 0) {
      const centerX = width / 2;
      const centerY = height / 2;
      const graphCenterX = graphNodes.reduce((sum, node) => sum + node.x, 0) / graphNodes.length;
      const graphCenterY = graphNodes.reduce((sum, node) => sum + node.y, 0) / graphNodes.length;
      
      setTransform({
        x: centerX - graphCenterX,
        y: centerY - graphCenterY,
        scale: 1
      });
    }
  }, [data, width, height]);

  const handleNodeClick = (nodeId: string) => {
    setSelectedNode(selectedNode === nodeId ? null : nodeId);
  };

  const handleNodeMouseEnter = (node: GraphNode, event: React.MouseEvent) => {
    const rect = svgRef.current?.getBoundingClientRect();
    if (rect) {
      const x = event.clientX - rect.left + 10;
      const y = event.clientY - rect.top - 10;
      
      const content = `
        <div class="text-sm">
          <div class="font-bold mb-1">${node.normalized_name || node.name}</div>
          <div class="text-xs text-gray-600 mb-1">GTIN: ${node.gtin}</div>
          ${node.product_type ? `<div class="text-xs">Type: ${node.product_type}</div>` : ''}
          ${node.gpc_code ? `<div class="text-xs">GPC: ${node.gpc_code}</div>` : ''}
          ${node.family_title ? `<div class="text-xs">Family: ${node.family_title}</div>` : ''}
          <div class="text-xs mt-1">
            ${node.nutrient_available ? '<span class="text-green-600">✓ Nutrition</span>' : '<span class="text-gray-400">✗ Nutrition</span>'}
            ${node.allergen_available ? '<span class="text-yellow-600 ml-2">✓ Allergen</span>' : '<span class="text-gray-400 ml-2">✗ Allergen</span>'}
          </div>
        </div>
      `;
      
      setTooltip({ show: true, content, x, y });
    }
  };

  const handleNodeMouseLeave = () => {
    setTooltip({ show: false, content: '', x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) { // Left click only
      setIsDragging(true);
      setDragStart({ x: e.clientX - transform.x, y: e.clientY - transform.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setTransform({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
        scale: transform.scale
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const scale = Math.max(0.1, Math.min(3, transform.scale - e.deltaY * 0.001));
    setTransform({
      ...transform,
      scale
    });
  };

  const resetView = () => {
    if (graphNodes.length > 0) {
      const centerX = width / 2;
      const centerY = height / 2;
      const graphCenterX = graphNodes.reduce((sum, node) => sum + node.x, 0) / graphNodes.length;
      const graphCenterY = graphNodes.reduce((sum, node) => sum + node.y, 0) / graphNodes.length;
      
      setTransform({
        x: centerX - graphCenterX,
        y: centerY - graphCenterY,
        scale: 1
      });
    }
  };

  const nodeRadius = 35;

  return (
    <div 
      ref={containerRef}
      className="relative border border-gray-300 rounded-lg bg-white overflow-hidden"
      style={{ width, height }}
    >
      {/* Controls */}
      <div className="absolute top-2 right-2 z-10">
        <button
          onClick={resetView}
          className="bg-white border border-gray-300 rounded px-2 py-1 text-xs hover:bg-gray-50"
          title="Reset view"
        >
          Reset
        </button>
      </div>
      
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className={`cursor-${isDragging ? 'grabbing' : 'grab'}`}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        style={{ userSelect: 'none' }}
      >
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" fill="#2B7CE9" />
          </marker>
        </defs>
        
        <g transform={`translate(${transform.x}, ${transform.y}) scale(${transform.scale})`}>
          {/* Links */}
          {graphLinks.map((link, index) => {
            const sourceNode = graphNodes.find(n => n.id === link.source);
            const targetNode = graphNodes.find(n => n.id === link.target);
            
            if (!sourceNode || !targetNode) return null;
            
            return (
              <g key={`link-${index}`}>
                <line
                  x1={sourceNode.x}
                  y1={sourceNode.y}
                  x2={targetNode.x}
                  y2={targetNode.y}
                  stroke="#2B7CE9"
                  strokeWidth={2}
                  markerEnd="url(#arrowhead)"
                />
                <text
                  x={(sourceNode.x + targetNode.x) / 2}
                  y={(sourceNode.y + targetNode.y) / 2}
                  textAnchor="middle"
                  dy={-5}
                  fontSize="10"
                  fill="#666"
                  className="pointer-events-none"
                >
                  {link.type}
                </text>
              </g>
            );
          })}
          
          {/* Nodes */}
          {graphNodes.map((node) => {
            const isSelected = selectedNode === node.id;
            const isHighlighted = selectedNode && (
              selectedNode === node.id ||
              graphLinks.some(link => 
                (link.source === selectedNode && link.target === node.id) ||
                (link.target === selectedNode && link.source === node.id)
              )
            );
            const label = node.normalized_name || node.name || '';
            return (
              <g 
                key={node.id} 
                onClick={() => handleNodeClick(node.id)}
                onMouseEnter={(e) => handleNodeMouseEnter(node, e)}
                onMouseLeave={handleNodeMouseLeave}
              >
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={nodeRadius}
                  fill={isSelected ? "#3B82F6" : isHighlighted ? "#93C5FD" : "#E5E7EB"}
                  stroke={isSelected ? "#1D4ED8" : "#9CA3AF"}
                  strokeWidth={isSelected ? 3 : 2}
                  className="cursor-pointer hover:stroke-blue-500 transition-colors"
                />
                <text
                  x={node.x}
                  y={node.y - 8}
                  textAnchor="middle"
                  fontSize="10"
                  fontWeight="bold"
                  fill={isSelected ? "white" : "#374151"}
                  className="pointer-events-none"
                >
                  {label.length > 12 ? label.substring(0, 12) + '...' : label}
                </text>
                <text
                  x={node.x}
                  y={node.y + 12}
                  textAnchor="middle"
                  fontSize="8"
                  fill={isSelected ? "white" : "#6B7280"}
                  className="pointer-events-none"
                >
                  {node.gtin}
                </text>
                {/* Additional info indicators */}
                {node.nutrient_available && (
                  <circle
                    cx={node.x - 15}
                    cy={node.y - 15}
                    r="3"
                    fill="#10B981"
                    className="pointer-events-none"
                  />
                )}
                {node.allergen_available && (
                  <circle
                    cx={node.x + 15}
                    cy={node.y - 15}
                    r="3"
                    fill="#F59E0B"
                    className="pointer-events-none"
                  />
                )}
              </g>
            );
          })}
        </g>
      </svg>
      
      {/* Tooltip */}
      {tooltip.show && (
        <div 
          className="absolute z-20 bg-white border border-gray-300 rounded-lg shadow-lg p-2 max-w-xs"
          style={{ 
            left: tooltip.x, 
            top: tooltip.y,
            transform: 'translateY(-100%)'
          }}
          dangerouslySetInnerHTML={{ __html: tooltip.content }}
        />
      )}
      
      {/* Instructions */}
      <div className="absolute bottom-2 left-2 text-xs text-gray-500 bg-white bg-opacity-90 px-2 py-1 rounded">
        Drag to pan • Scroll to zoom • Click nodes to highlight • Hover for details
      </div>
      
      {/* Legend */}
      <div className="absolute top-2 left-2 text-xs text-gray-600 bg-white bg-opacity-90 px-2 py-1 rounded">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
          <span>Nutrition data</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
          <span>Allergen data</span>
        </div>
      </div>
    </div>
  );
};

export default HierarchyGraph; 