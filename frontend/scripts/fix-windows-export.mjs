// Works around a Windows-only bug in Next.js static export (16.4): segment prefetch files
// should be named like `activity/__next.activity.__PAGE__.txt`, but the exporter only
// replaces "/" with "." while Windows paths use "\", so it writes
// `activity/__next.activity/__PAGE__.txt` instead and prefetches get 404s.
// (node_modules/next/dist/export/index.js → convertSegmentPathToStaticExportFilename)
// Linux builds (Docker, CI) are correct, so this script does nothing there.
import { readdirSync, renameSync, rmdirSync, statSync } from "node:fs";
import { join } from "node:path";

if (process.platform === "win32") {
  const fixed = [];
  const walk = (dir) => {
    for (const name of readdirSync(dir)) {
      const path = join(dir, name);
      if (!statSync(path).isDirectory()) continue;
      if (name.startsWith("__next.")) flatten(path, name, dir);
      else walk(path);
    }
  };
  const flatten = (path, prefix, parent) => {
    for (const name of readdirSync(path)) {
      const child = join(path, name);
      if (statSync(child).isDirectory()) flatten(child, `${prefix}.${name}`, parent);
      else {
        renameSync(child, join(parent, `${prefix}.${name}`));
        fixed.push(join(parent, `${prefix}.${name}`));
      }
    }
    rmdirSync(path);
  };
  walk("out");
  console.log(`fix-windows-export: renamed ${fixed.length} prefetch file(s)`);
}
