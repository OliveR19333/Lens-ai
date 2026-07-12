import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import { Suspense, useRef, useEffect } from 'react';

function RotatingBox() {
  const meshRef = useRef(null);

  useEffect(() => {
    const mesh = meshRef.current;
    if (!mesh) return;

    const animate = () => {
      mesh.rotation.x += 0.01;
      mesh.rotation.y += 0.015;
      requestAnimationFrame(animate);
    };

    const id = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(id);
  }, []);

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[2, 2, 2]} />
      <meshPhongMaterial color="#6366f1" />
    </mesh>
  );
}

function RotatingIcosahedron() {
  const meshRef = useRef(null);

  useEffect(() => {
    const mesh = meshRef.current;
    if (!mesh) return;

    const animate = () => {
      mesh.rotation.x += 0.005;
      mesh.rotation.y += 0.01;
      mesh.rotation.z += 0.003;
      requestAnimationFrame(animate);
    };

    const id = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(id);
  }, []);

  return (
    <mesh ref={meshRef} position={[0, 0, 0]}>
      <icosahedronGeometry args={[1.5, 4]} />
      <meshPhongMaterial color="#ec4899" wireframe={false} />
    </mesh>
  );
}

export default function Scene3D() {
  return (
    <div className="w-full h-96 rounded-lg overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 border border-secondary/30">
      <Canvas>
        <PerspectiveCamera makeDefault position={[0, 0, 5]} />
        <ambientLight intensity={0.6} />
        <pointLight position={[10, 10, 10]} intensity={0.8} />
        <pointLight position={[-10, -10, 5]} intensity={0.4} color="#ec4899" />

        <Suspense fallback={null}>
          <RotatingBox />
          <RotatingIcosahedron />
        </Suspense>

        <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={3} />
      </Canvas>
    </div>
  );
}
