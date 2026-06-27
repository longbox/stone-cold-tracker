import { GoogleGenAI } from '@google/genai';
import { NextResponse } from 'next/server';

// Initialize the SDK. It automatically picks up process.env.GEMINI_API_KEY
const ai = new GoogleGenAI({});

export async function POST(req) {
  try {
    const formData = await req.formData();
    const imageFile = formData.get('image');

    if (!imageFile) {
      return NextResponse.json({ error: 'No image provided' }, { status: 400 });
    }

    // Convert the File object to base64
    const buffer = Buffer.from(await imageFile.arrayBuffer());
    
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: [
        {
          role: 'user',
          parts: [
            { text: 'Analyze this image of food or ingredients. List the identified ingredients and provide an estimation of their oxalate content (Low, Medium, High). Format the output clearly with bullet points. Be concise but informative.' },
            { 
              inlineData: {
                data: buffer.toString('base64'),
                mimeType: imageFile.type,
              }
            }
          ]
        }
      ]
    });

    return NextResponse.json({ analysis: response.text });
  } catch (error) {
    console.error('Error analyzing image:', error);
    return NextResponse.json(
      { error: 'Failed to analyze image. Please ensure your GEMINI_API_KEY is configured correctly.' },
      { status: 500 }
    );
  }
}
