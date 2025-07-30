import React, { useEffect, useRef, useState } from 'react';

interface HierarchyNode {
  gtin: string;
  name: string;
  normalized_name?: string;
  product_type?: string;
  gpc_code?: string;
  family_title?: string;
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

interface GraphNode extends HierarchyNode {
  id: string;
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
    if (!data || !Array.isArray(data.nodes) || data.nodes.length === 0) {
      setGraphNodes([]);
      setGraphLinks([]);
      return;
    }
    const { nodes, relationships } = data;
    // Assign levels using BFS
    const levels = new Map<string, number>();
    const children = new Map<string, string[]>();
    relationships.forEach(rel => {
      if (!children.has(rel.source)) children.set(rel.source, []);
      children.get(rel.source)!.push(rel.target);
    });
    const targetGtins = new Set(relationships.map(rel => rel.target));
    const rootGtins = nodes.map(node => node.gtin).filter(gtin => !targetGtins.has(gtin));
    const queue: { gtin: string; level: number }[] = rootGtins.map(gtin => ({ gtin, level: 0 }));
    const visited = new Set<string>();
    while (queue.length > 0) {
      const { gtin, level } = queue.shift()!;
      if (visited.has(gtin)) continue;
      visited.add(gtin);
      levels.set(gtin, level);
      (children.get(gtin) || []).forEach(childGtin => {
        queue.push({ gtin: childGtin, level: level + 1 });
      });
    }
    // Assign positions
    const nodesPerLevel = new Map<number, string[]>();
    nodes.forEach(node => {
      const level = levels.get(node.gtin) || 0;
      if (!nodesPerLevel.has(level)) nodesPerLevel.set(level, []);
      nodesPerLevel.get(level)!.push(node.gtin);
    });
    const nodeRadius = 50;
    const graphNodes: GraphNode[] = nodes.map(node => {
      const level = levels.get(node.gtin) || 0;
      const levelNodes = nodesPerLevel.get(level) || [];
      const nodeIndex = levelNodes.indexOf(node.gtin);
      const levelWidth = Math.max(levelNodes.length, 1);
      const spacing = Math.max(120, width * 0.8 / levelWidth);
      const x = spacing * (nodeIndex + 1) + width * 0.1;
      const y = (height * 0.8 / (Math.max(...Array.from(nodesPerLevel.keys())) + 1)) * (level + 1) + height * 0.1;
      return {
        ...node,
        id: node.gtin,
        x,
        y,
        level
      };
    });
    setGraphNodes(graphNodes);
    setGraphLinks(relationships);
    // Center the graph
    if (graphNodes.length > 0) {
      const centerX = width / 2;
      const centerY = height / 2;
      const graphCenterX = graphNodes.reduce((sum, node) => sum + node.x, 0) / graphNodes.length;
      const graphCenterY = graphNodes.reduce((sum, node) => sum + node.y, 0) / graphNodes.length;
      setTransform({ x: centerX - graphCenterX, y: centerY - graphCenterY, scale: 1 });
    }
  }, [data, width, height]);

  const nodeRadius = 50;

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
        </div>
      `;
      setTooltip({ show: true, content, x, y });
    }
  };

  const handleNodeMouseLeave = () => {
    setTooltip({ show: false, content: '', x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) {
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
    setTransform({ ...transform, scale });
  };

  const resetView = () => {
    if (graphNodes.length > 0) {
      const centerX = width / 2;
      const centerY = height / 2;
      const graphCenterX = graphNodes.reduce((sum, node) => sum + node.x, 0) / graphNodes.length;
      const graphCenterY = graphNodes.reduce((sum, node) => sum + node.y, 0) / graphNodes.length;
      setTransform({ x: centerX - graphCenterX, y: centerY - graphCenterY, scale: 1 });
    }
  };

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
            // Calculate control points for curved lines to avoid intersections
            const dx = targetNode.x - sourceNode.x;
            const dy = targetNode.y - sourceNode.y;
            const midX = sourceNode.x + dx * 0.5;
            const midY = sourceNode.y + dy * 0.5;
            const offset = Math.min(30, Math.abs(dx) * 0.3);
            // Create curved path
            const path = `M ${sourceNode.x} ${sourceNode.y} Q ${midX} ${midY - offset} ${targetNode.x} ${targetNode.y}`;
            return (
              <g key={`link-${index}`}>
                <path
                  d={path}
                  stroke="#2B7CE9"
                  strokeWidth={2}
                  fill="none"
                  markerEnd="url(#arrowhead)"
                />
                <text
                  x={midX}
                  y={midY - offset - 5}
                  textAnchor="middle"
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
          {graphNodes.map((node, index) => {
            const isSelected = selectedNode === node.id;
            const label = node.normalized_name || node.name || '';
            return (
              <g
                key={node.id}
                onClick={() => handleNodeClick(node.id)}
                onMouseEnter={e => handleNodeMouseEnter(node, e)}
                onMouseLeave={handleNodeMouseLeave}
              >
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={nodeRadius}
                  fill={isSelected ? "#3B82F6" : "#E5E7EB"}
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
              </g>
            );
          })}
        </g>
      </svg>
      {/* Tooltip */}
      {tooltip.show && (
        <div
          className="absolute z-20 pointer-events-none"
          style={{ left: tooltip.x, top: tooltip.y }}
          dangerouslySetInnerHTML={{ __html: tooltip.content }}
        />
      )}
    </div>
  );
};

export default HierarchyGraph; 