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
            { text: 'Analyze this image of food or ingredients. List the identified ingredients and provide an estimation of their oxalate content (Low, Medium, High). Cross-reference with modern research, including the Harvard oxalate database and recent testing advancements (e.g., recognizing blueberries as moderate/high, not low). Return the output as valid JSON with exactly two fields: "analysis_text" containing the detailed markdown analysis with bullet points, and "oxalate_score" containing an integer from 0 to 100 representing the overall oxalate level (0 being completely free of oxalates, 100 being dangerously high). Do NOT wrap the JSON in markdown code blocks.' },
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

    let resultData;
    try {
      resultData = JSON.parse(response.text);
    } catch (e) {
      console.warn("Failed to parse JSON, falling back to raw text:", e);
      resultData = { analysis_text: response.text, oxalate_score: 50 };
    }

    return NextResponse.json({ analysis: resultData });
  } catch (error) {
    console.error('Error analyzing image:', error);
    return NextResponse.json(
      { error: 'Failed to analyze image. Please ensure your GEMINI_API_KEY is configured correctly.' },
      { status: 500 }
    );
  }
}
