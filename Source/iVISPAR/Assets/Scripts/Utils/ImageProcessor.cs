using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public static class ImageProcessor
{
    public static byte[] FlipTopBottom(byte[] imageData)
    {
        // Step 1: Load the byte array as a Texture2D
        Texture2D texture = new Texture2D(2, 2);
        texture.LoadImage(imageData); // Automatically resizes the texture

        // Step 2: Flip the texture vertically
        FlipTextureVertically(texture);

        // Step 3: Encode the flipped Texture2D back to a byte array
        return texture.EncodeToPNG(); // Or EncodeToJPG() depending on your format
    }

    private static void FlipTextureVertically(Texture2D texture)
    {
        int width = texture.width;
        int height = texture.height;
        Color[] originalPixels = texture.GetPixels();

        Color[] flippedPixels = new Color[originalPixels.Length];
        for (int y = 0; y < height; y++)
        {
            // Copy each row of pixels from the top to the bottom
            int originalRow = y * width;
            int flippedRow = (height - 1 - y) * width;
            System.Array.Copy(originalPixels, originalRow, flippedPixels, flippedRow, width);
        }

        // Apply the flipped pixels back to the texture
        texture.SetPixels(flippedPixels);
        texture.Apply();
    }
}