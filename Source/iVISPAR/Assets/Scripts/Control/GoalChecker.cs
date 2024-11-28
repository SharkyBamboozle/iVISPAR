using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace GameLogic
{
    public class GoalChecker 
    {
        public bool CheckAllObjects()
        {
            // Find all objects tagged as "Commandable"
            GameObject[] objects = GameObject.FindGameObjectsWithTag("Commandable");

            foreach (GameObject obj in objects)
            {
                // Get the TargetBehaviour component from the object
                TargetBehaviour targetBehaviour = obj.GetComponent<TargetBehaviour>();

                if (targetBehaviour != null && targetBehaviour.gridBoard != null)
                {
                    // Get the current position in the world and convert it to grid coordinates
                    Vector3 worldPos = obj.transform.position;
                    int currentGridX, currentGridZ;
                    targetBehaviour.gridBoard.grid.GetGridPosition(worldPos, out currentGridX, out currentGridZ);  // Convert world position to grid coordinates

                    // Get the goal position from TargetBehaviour (already in grid coordinates)
                    Vector2 goalGridPos = targetBehaviour.goalCoordinate;
                    //Vector2Int goalGridPos = new Vector2Int(targetBehaviour.goal_x, targetBehaviour.goal_y);

                    // Compare the current grid position with the goal position
                    if (currentGridX != goalGridPos.x || currentGridZ != goalGridPos.y)
                    {
                        // Log the mismatch and return false
                        Debug.Log($"Object at grid position ({currentGridX}, {currentGridZ}) does not match goal grid position {goalGridPos}");
                        return false;
                    }
                }
            }

            // If all objects match their goal coordinates, return true
            Debug.Log("All objects match their goal coordinates!");
            return true;
        }

        private bool ApproximatelyEqual(Vector2 a, Vector2 b, float tolerance = 0.01f)
        {
            return Vector2.Distance(a, b) < tolerance;
        }
    }
}