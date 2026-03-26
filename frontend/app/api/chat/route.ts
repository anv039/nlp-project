import { NextRequest, NextResponse } from 'next/server';
import { spawnSync } from 'child_process';
import path from 'path';

const PYTHON_PATH = path.join(process.cwd(), '../nlp_env/bin/python');
const CHAT_PATH = path.join(process.cwd(), '../q4/chatbot.py');

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const message = formData.get('message') as string;
    const historyStr = formData.get('history') as string;
    const history = JSON.parse(historyStr || '[]');
    const { stdout, stderr } = spawnSync(PYTHON_PATH, [path.join(process.cwd(), '../q4/run_chat.py')], {
      input: JSON.stringify({
        message,
        history
      }),
      encoding: 'utf8',
      timeout: 60000
    });
    
    console.log('Python stdout:', stdout.trim());
    console.log('Python stderr:', stderr.toString());
    
    if (!stdout.trim()) {
      throw new Error(`No output from Python. Check logs.`);
    }
    
    const result = JSON.parse(stdout.trim());
    return NextResponse.json({ success: true, data: result });
  } catch (error: any) {
    return NextResponse.json({ response: error.message, intent: 'error', confidence: 0.0 }, { status: 500 });
  }
}

