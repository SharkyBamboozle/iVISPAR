using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;
using Unity.VisualScripting;

public class TileLabel : MonoBehaviour
{
    // Start is called before the first frame update
     public Vector3 LableOffset = new Vector3(1.0f,0.55f,-0.25f);
     private string label;
     public int fontSize = 4;
    public float labelSize = 1f;
    public void CreateLabel()
    {
        
        label = gameObject.GetComponent<TargetBehaviour>().getGeomNumber();
        GameObject myTextObject = new GameObject(label);
        myTextObject.transform.SetParent(this.transform);
        myTextObject.transform.Rotate(new Vector3(90,0,0));
        myTextObject.transform.localPosition = LableOffset;
        myTextObject.AddComponent<TextMeshPro>();
        TextMeshPro textMeshComponent = myTextObject.GetComponent<TextMeshPro>();
        textMeshComponent.rectTransform.SetSizeWithCurrentAnchors(RectTransform.Axis.Horizontal,labelSize);
        textMeshComponent.rectTransform.SetSizeWithCurrentAnchors(RectTransform.Axis.Vertical,labelSize);
        textMeshComponent.text = label;
        textMeshComponent.fontSize = fontSize;
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
