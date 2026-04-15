import { OrbitControls } from "@react-three/drei";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef } from "react";
import * as THREE from "three";

export type PointCloudLayer = {
  points: [number, number, number][];
  color: string;
  size?: number;
};

type Props = {
  layers: PointCloudLayer[];
  emptyMessage: string;
  pointScale?: number;
  resetToken?: number;
};

function normalizeLayers(layers: PointCloudLayer[]) {
  const allPoints = layers.flatMap((layer) => layer.points);
  if (allPoints.length === 0) {
    return layers;
  }

  let minX = Infinity;
  let minY = Infinity;
  let minZ = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  let maxZ = -Infinity;

  for (const [x, y, z] of allPoints) {
    if (x < minX) minX = x;
    if (y < minY) minY = y;
    if (z < minZ) minZ = z;
    if (x > maxX) maxX = x;
    if (y > maxY) maxY = y;
    if (z > maxZ) maxZ = z;
  }

  const centerX = (minX + maxX) / 2;
  const centerY = (minY + maxY) / 2;
  const centerZ = (minZ + maxZ) / 2;
  const maxRange = Math.max(maxX - minX, maxY - minY, maxZ - minZ, 1e-6);
  const scale = 2 / maxRange;

  return layers.map((layer) => ({
    ...layer,
    points: layer.points.map(([x, y, z]) => [
      (x - centerX) * scale,
      (y - centerY) * scale,
      (z - centerZ) * scale
    ])
  }));
}

function PointLayer({ layer, pointScale }: { layer: PointCloudLayer; pointScale: number }) {
  const positions = useMemo(() => {
    const data = new Float32Array(layer.points.length * 3);
    layer.points.forEach(([x, y, z], index) => {
      const offset = index * 3;
      data[offset] = x;
      data[offset + 1] = y;
      data[offset + 2] = z;
    });
    return data;
  }, [layer.points]);

  return (
    <points>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" array={positions} count={layer.points.length} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial color={layer.color} size={(layer.size ?? 0.035) * pointScale} sizeAttenuation />
    </points>
  );
}

function AutoRotateGroup({ children }: { children: React.ReactNode }) {
  const ref = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (!ref.current) return;
    ref.current.rotation.y += delta * 0.18;
  });

  return <group ref={ref}>{children}</group>;
}

function CameraResetter({
  resetToken,
  controlsRef
}: {
  resetToken: number;
  controlsRef: React.MutableRefObject<any>;
}) {
  const { camera } = useThree();

  useEffect(() => {
    camera.position.set(0.5, 0.6, 2.2);
    camera.lookAt(0, 0, 0);
    if (controlsRef.current) {
      controlsRef.current.target.set(0, 0, 0);
      controlsRef.current.update();
    }
  }, [camera, controlsRef, resetToken]);

  return null;
}

export function PointCloudViewer({ layers, emptyMessage, pointScale = 1, resetToken = 0 }: Props) {
  const visibleLayers = useMemo(() => layers.filter((layer) => layer.points.length > 0), [layers]);
  const normalizedLayers = useMemo(() => normalizeLayers(visibleLayers), [visibleLayers]);
  const controlsRef = useRef<any>(null);

  if (normalizedLayers.length === 0) {
    return <div className="point-cloud-empty">{emptyMessage}</div>;
  }

  return (
    <div className="point-cloud-card">
      <Canvas camera={{ position: [0.5, 0.6, 2.2], fov: 42 }}>
        <color attach="background" args={["#0d1016"]} />
        <ambientLight intensity={1.6} />
        <gridHelper args={[4, 8, "#32445f", "#1d2a3a"]} />
        <axesHelper args={[1.8]} />
        <CameraResetter resetToken={resetToken} controlsRef={controlsRef} />
        <AutoRotateGroup>
          {normalizedLayers.map((layer, index) => (
            <PointLayer key={`${layer.color}-${index}-${layer.points.length}`} layer={layer} pointScale={pointScale} />
          ))}
        </AutoRotateGroup>
        <OrbitControls ref={controlsRef} enablePan enableZoom enableRotate minDistance={1.2} maxDistance={8} />
      </Canvas>
    </div>
  );
}
