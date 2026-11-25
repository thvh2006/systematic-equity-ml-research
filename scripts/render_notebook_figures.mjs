import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import sharp from 'sharp';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),out=path.join(root,'artifacts/review/figures');await fs.mkdir(out,{recursive:true});let count=0;
for(const filename of await fs.readdir(path.join(root,'notebooks'))){if(!/^0[1-8]_/.test(filename)||filename.includes('foundation'))continue;const nb=JSON.parse(await fs.readFile(path.join(root,'notebooks',filename),'utf8'));for(const c of nb.cells)for(const o of c.outputs||[]){const svg=o.data?.['image/svg+xml'];if(!svg)continue;const key=crypto.createHash('sha256').update(svg).digest('hex');await sharp(Buffer.from(svg),{density:144}).png().toFile(path.join(out,key+'.png'));count++;}}
console.log(JSON.stringify({rendered:count,directory:out}));
