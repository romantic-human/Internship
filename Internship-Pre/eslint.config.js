import js from "@eslint/js";
import pluginVue from "eslint-plugin-vue";
import vueParser from "vue-eslint-parser";
import tsParser from "@typescript-eslint/parser";
import tsPlugin from "@typescript-eslint/eslint-plugin";
import prettierPlugin from "eslint-plugin-prettier";

export default [
  // 全局忽略
  { ignores: ["dist/**", "node_modules/**", "*.min.js"] },

  // 基础 JS 推荐规则
  js.configs.recommended,

  // Vue 推荐规则
  ...pluginVue.configs["flat/recommended"],

  // TypeScript 文件配置
  {
    files: ["**/*.{ts,tsx,vue}"],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tsParser,
        ecmaVersion: "latest",
        sourceType: "module",
        extraFileExtensions: [".vue"],
      },
      globals: {
        // 浏览器环境
        window: "readonly",
        document: "readonly",
        console: "readonly",
        localStorage: "readonly",
        sessionStorage: "readonly",
        fetch: "readonly",
        setTimeout: "readonly",
        clearTimeout: "readonly",
        setInterval: "readonly",
        clearInterval: "readonly",
        requestAnimationFrame: "readonly",
        ResizeObserver: "readonly",
        HTMLElement: "readonly",
        HTMLDivElement: "readonly",
      },
    },
    plugins: {
      "@typescript-eslint": tsPlugin,
      prettier: prettierPlugin,
    },
    rules: {
      // TypeScript 规则
      "@typescript-eslint/no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/consistent-type-imports": "error",

      // Vue 规则调整
      "vue/multi-word-component-names": "off",
      "vue/no-v-html": "off",
      "vue/attribute-hyphenation": "error",
      "vue/v-on-event-hyphenation": "error",
      "vue/max-attributes-per-line": "off",
      "vue/singleline-html-element-content-newline": "off",
      "vue/html-self-closing": "off",

      // 通用规则
      "no-console": ["warn", { allow: ["warn", "error"] }],
      "no-debugger": "warn",
      "no-unused-vars": "off", // 由 @typescript-eslint 接管
      "prefer-const": "error",
      "no-var": "error",
      "eqeqeq": ["error", "always"],

      // Prettier 集成
      "prettier/prettier": [
        "warn",
        {
          semi: true,
          singleQuote: false,
          tabWidth: 2,
          trailingComma: "all",
          printWidth: 120,
          endOfLine: "auto",
        },
      ],
    },
  },
];
