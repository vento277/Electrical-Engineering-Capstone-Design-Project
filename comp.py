import open3d as o3d
import numpy as np

def conv_ply(file_path):
    """Convert to ASCII format."""
    pcd = o3d.io.read_point_cloud(file_path)
    
    # Invert the z values
    points = np.asarray(pcd.points)
    points[:, 2] = -points[:, 2]  # Invert the z-axis
    pcd.points = o3d.utility.Vector3dVector(points)
    
    o3d.io.write_point_cloud(file_path, pcd, write_ascii=True)
    
def reorder_ply(file_path):
    """Reorder coordinate data in ascending order of x"""
    

def load_ply(file_path):
    """Load a .ply file and return its point cloud."""
    pcd = o3d.io.read_point_cloud(file_path)
    return np.asarray(pcd.points)

def compute_accuracy(ground_truth, prediction):
    """
    Compute accuracy by comparing the ground truth and prediction point clouds.
    This example uses Mean Squared Error (MSE) as a metric.
    """
    if ground_truth.shape != prediction.shape:
        raise ValueError("Point clouds must have the same shape for comparison.")
    
    mse = np.mean((ground_truth - prediction) ** 2)
    return mse

if __name__ == "__main__":
    # File paths
    ground_truth_path = "outputs/rs/test.ply"
    prediction_path = "outputs/da/test.ply"
    
    # Convert to ASCII format
    conv_ply(prediction_path)

    # Load point clouds
    ground_truth = load_ply(ground_truth_path)
    prediction = load_ply(prediction_path)

    # Compute accuracy
    accuracy = compute_accuracy(ground_truth, prediction)
    print(f"Accuracy (MSE): {accuracy}")