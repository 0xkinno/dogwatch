/** @type {import('next').NextConfig} */
import path from "node:path";
import { fileURLToPath } from "node:url";
const here = path.dirname(fileURLToPath(import.meta.url));
const nextConfig = { reactStrictMode: true, outputFileTracingRoot: here };
export default nextConfig;
