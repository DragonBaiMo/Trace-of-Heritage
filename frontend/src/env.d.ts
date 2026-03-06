/// <reference types="vite/client" />

// 让 TypeScript 识别 .vue 单文件组件的模块类型
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
