/// <reference types="vite/client" />
/// <reference types="vite-plugin-pwa/client" />
import 'react';
import type { ThreeElements } from '@react-three/fiber';

interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare module 'react' {
  namespace JSX {
    interface IntrinsicElements extends ThreeElements {}
  }
}
