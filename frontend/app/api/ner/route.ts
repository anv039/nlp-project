import { NextRequest, NextResponse } from 'next/server';
import { spawnSync } from 'child_process';
import path from 'path';
import fs from 'fs/promises';
import os from 'os';

const PYTHON_PATH = path.join(process.cwd(), '../nlp_env/bin/python');
const NER_PATH = path.join(process.cwd(), '../q3/spacy_ner.py');

export async function POST(req: NextRequest) {
  try {
    const contentType = req.headers.get('content-type') || '';
    if (contentType.includes('multipart/form-data')) {
      const formData = await req.formData();
      const file = formData.get('file') as File;
      if (!file) {
        return NextResponse.json({ error: 'No file' }, { status: 400 });
      }
      const bytes = await file.arrayBuffer();
      const buffer = Buffer.from(bytes);
      const tempPath = path.join(os.tmpdir(), `ner_${Date.now()}.csv`);
      await fs.writeFile(tempPath, buffer);
      try {
        const { stdout } = spawnSync(PYTHON_PATH, [NER_PATH], {
          input: JSON.stringify({ mode: 'csv', file_path: tempPath }),
          encoding: 'utf8',
          timeout: 30000
        });
        const result = JSON.parse(stdout.trim());
        return NextResponse.json(result);
      } finally {
        fs.unlink(tempPath).catch(() => {});
      }
    } else {
      const data = await req.json();
      const { stdout } = spawnSync(PYTHON_PATH, [NER_PATH], {
        input: JSON.stringify({ mode: 'text', text: data.text }),
        encoding: 'utf8',
        timeout: 30000
      });
      const result = JSON.parse(stdout.trim());
      return NextResponse.json(result);
    }
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

