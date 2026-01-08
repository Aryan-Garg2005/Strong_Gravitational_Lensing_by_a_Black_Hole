import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

bg_img = Image.open("im.tif") #Load image
if bg_img.mode != "RGB":
    bg_img = bg_img.convert("RGB")

bg = np.array(bg_img).astype(np.float32)


bg = 255 * (bg - bg.min()) / (bg.max() - bg.min())
bg = bg.astype(np.uint8)

H, W, _ = bg.shape

M = 1.0
b_crit = 3 * np.sqrt(3) * M      # photon sphere
A = 1.4                          # strong-lensing strength
eps = 0.03                       # regularization scale

# Geometry
theta_max = 25.0
N = 1200

output = np.zeros((N, N, 3), dtype=np.float32)


def deflection_angle(b):
    return 4*M/b + A * np.log((b + eps) / (b - b_crit + eps))


for i in range(N):
    for j in range(N):
        x = (j - N/2) / (N/2) * theta_max
        y = (i - N/2) / (N/2) * theta_max

        theta = np.sqrt(x**2 + y**2)
        b = theta
        if b <= b_crit:
            output[i, j] = 0
            continue
        pixel_color = np.zeros(3)
        weight_sum = 0.0

        for n in [0, 1, 2]:
            alpha = deflection_angle(b) + 2*np.pi*n

            beta_x = x - alpha * x / theta
            beta_y = y - alpha * y / theta

            u = int((beta_x / theta_max + 0.5) * W) % W
            v = int((beta_y / theta_max + 0.5) * H) % H

            w = np.exp(-1*n)

            pixel_color[0] += w * bg[v, u, 0] * (1 + 0.04*n)
            pixel_color[1] += w * bg[v, u, 1]
            pixel_color[2] += w * bg[v, u, 2] * (1 - 0.04*n)

            weight_sum += w

        output[i, j] = pixel_color / weight_sum


plt.figure(figsize=(9, 9))
output = np.power(output / 255.0, 0.85) * 255
plt.imshow(output.astype(np.uint8))
plt.axis("off")
plt.title("Strong Gravitational Lensing with Photon Sphere")
plt.show()

