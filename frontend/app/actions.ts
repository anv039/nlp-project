'use server';

import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import os from 'os';

export type NERResult = {
  entities: {
    PERSON: string[];
    ORGANIZATION: string[];
    LOCATION: string[];
  };
  counts: {
    PERSON: number;
    ORGANIZATION: number;
    LOCATION: number;
  };
  text: string;
};

export type CSVResult = {
  results: Array<{
    text: string;
    counts: {
      PERSON: number;
      ORGANIZATION: number;
      LOCATION: number;
    };
  }>;
};

export type ChatResult = {
  response: string;
  intent: string;
  confidence: number;
};

const PYTHON_PATH = path.join(process.cwd(), '../nlp_env/bin/python');
const NER_PATH = path.join(process.cwd(), '../q3/run_ner.py');
const CHAT_PATH = path.join(process.cwd(), '../q4/run_chat.py');

import { spawnSync } from 'child_process';

async function runPython(scriptPath: string, inputData: any): Promise<any> {
  const { stdout, stderr } = spawnSync(PYTHON_PATH, [scriptPath], {


    input: JSON.stringify(inputData) + '\n',
    encoding: 'utf8',
    timeout: 60000,  // 60s for spacy
  });
  if (!stdout.trim()) throw new Error(`Python stderr: ${stderr.toString()}`);

  return JSON.parse(stdout.trim());
}

export async function analyzeNER(formData: FormData) {
  try {
    const mode = formData.get('mode') as string;
    if (mode === 'text') {
      const text = formData.get('text') as string;
      const result = await runPython(NER_PATH, { mode: 'text', text });
      return { success: true, data: result } as { success: true; data: NERResult };
    } else if (mode === 'csv') {
      const file = formData.get('file') as File;
      if (!file) throw new Error('No file');
      const bytes = await file.arrayBuffer();
      const tempPath = path.join(os.tmpdir(), `ner_${Date.now()}.csv`);
      await fs.writeFile(tempPath, Buffer.from(bytes));
      try {
        const result = await runPython(NER_PATH, { mode: 'csv', file_path: tempPath });
        return { success: true, data: result } as { success: true; data: CSVResult };
      } finally {
        await fs.unlink(tempPath).catch(console.error);
      }
    }
    throw new Error('Invalid mode');
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
  }
}

export async function sendChatMessage(formData: FormData) {
  try {
    const message = formData.get('message') as string;
    const history = JSON.parse(formData.get('history') as string || '[]');
    const result = await runPython(CHAT_PATH, { message, history });
    return { success: true, data: result } as { success: true; data: ChatResult };
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : 'Unknown error' } as { success: false; error: string };
  }
}

