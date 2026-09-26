import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models

def main():
    # 1. Hardware acceleration check
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # 2. Image Transformations
    # Satellite images are normalized using ImageNet stats for pre-trained weights
    transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                             std=[0.229, 0.224, 0.225])
    ])

    # 3. Load Dataset
    # Download the standard EuroSAT RGB zip file if not already present
    dataset_url = "https://dfki.de"
    data_dir = "./data"
    
    if not os.path.exists(data_dir):
        import urllib.request
        import zipfile
        print("Downloading EuroSAT Dataset...")
        os.makedirs(data_dir, exist_ok=True)
        zip_path = os.path.join(data_dir, "EuroSAT.zip")
        urllib.request.urlretrieve(dataset_url, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        print("Download and extraction complete.")

    # Target the extracted image directory
    extracted_path = os.path.join(data_dir, "27500")
    full_dataset = datasets.ImageFolder(root=extracted_path, transform=transform)
    
    # 4. Train/Validation Split (80/20 standard)
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False, num_workers=2)

    # 5. Define Model Structure
    # Modifying a pre-trained ResNet18 for the 10 structural EuroSAT classes
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 10) 
    model = model.to(device)

    # 6. Loss and Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # 7. Training Loop (Demonstration: 1 Epoch)
    print("Starting training...")
    model.train()
    for epoch in range(1):
        running_loss = 0.0
        correct = 0
        total = 0
        
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        epoch_loss = running_loss / len(train_loader.dataset)
        epoch_acc = (correct / total) * 100
        print(f"Epoch 1 Loss: {epoch_loss:.4f} | Accuracy: {epoch_acc:.2f}%")

    # 8. Validation Phase
    model.eval()
    val_correct = 0
    val_total = 0
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)
            val_total += labels.size(0)
            val_correct += (predicted == labels).sum().item()

    print(f"Validation Accuracy: {(val_correct / val_total) * 100:.2f}%")

if __name__ == '__main__':
    main()
