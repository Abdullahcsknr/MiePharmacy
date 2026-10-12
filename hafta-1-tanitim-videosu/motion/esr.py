"""Real-ESRGAN ile kare kare netleştirme (CPU). basicsr bağımlılığı olmadan model mimarileri burada.

Kullanım: python3 esr.py MODEL.pth GIRIS_DIR CIKIS_DIR [--model compact|x4plus] [--tile 256]
Giriş: *.jpg kareler. Çıkış: aynı adlarla 4x büyütülmüş kareler.
"""
import argparse, glob, os, time
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from PIL import Image


class SRVGGNetCompact(nn.Module):   # realesr-general-x4v3
    def __init__(self, nf=64, nc=32, up=4):
        super().__init__(); self.up = up
        b = [nn.Conv2d(3, nf, 3, 1, 1), nn.PReLU(nf)]
        for _ in range(nc): b += [nn.Conv2d(nf, nf, 3, 1, 1), nn.PReLU(nf)]
        b += [nn.Conv2d(nf, 3 * up * up, 3, 1, 1)]
        self.body = nn.ModuleList(b); self.upsampler = nn.PixelShuffle(up)

    def forward(self, x):
        o = x
        for m in self.body: o = m(o)
        return self.upsampler(o) + F.interpolate(x, scale_factor=self.up, mode="nearest")


class RDB(nn.Module):
    def __init__(self, nf=64, gc=32):
        super().__init__()
        self.conv1 = nn.Conv2d(nf, gc, 3, 1, 1); self.conv2 = nn.Conv2d(nf + gc, gc, 3, 1, 1)
        self.conv3 = nn.Conv2d(nf + 2 * gc, gc, 3, 1, 1); self.conv4 = nn.Conv2d(nf + 3 * gc, gc, 3, 1, 1)
        self.conv5 = nn.Conv2d(nf + 4 * gc, nf, 3, 1, 1); self.l = nn.LeakyReLU(0.2, True)

    def forward(self, x):
        x1 = self.l(self.conv1(x)); x2 = self.l(self.conv2(torch.cat((x, x1), 1)))
        x3 = self.l(self.conv3(torch.cat((x, x1, x2), 1))); x4 = self.l(self.conv4(torch.cat((x, x1, x2, x3), 1)))
        return self.conv5(torch.cat((x, x1, x2, x3, x4), 1)) * 0.2 + x


class RRDB(nn.Module):
    def __init__(self, nf=64):
        super().__init__(); self.rdb1, self.rdb2, self.rdb3 = RDB(nf), RDB(nf), RDB(nf)

    def forward(self, x): return self.rdb3(self.rdb2(self.rdb1(x))) * 0.2 + x


class RRDBNet(nn.Module):   # RealESRGAN_x4plus
    def __init__(self, nf=64, nb=23):
        super().__init__()
        self.conv_first = nn.Conv2d(3, nf, 3, 1, 1); self.body = nn.Sequential(*[RRDB(nf) for _ in range(nb)])
        self.conv_body = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_up1 = nn.Conv2d(nf, nf, 3, 1, 1); self.conv_up2 = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_hr = nn.Conv2d(nf, nf, 3, 1, 1); self.conv_last = nn.Conv2d(nf, 3, 3, 1, 1); self.l = nn.LeakyReLU(0.2, True)

    def forward(self, x):
        f = self.conv_first(x); f = f + self.conv_body(self.body(f))
        f = self.l(self.conv_up1(F.interpolate(f, scale_factor=2, mode="nearest")))
        f = self.l(self.conv_up2(F.interpolate(f, scale_factor=2, mode="nearest")))
        return self.conv_last(self.l(self.conv_hr(f)))


def run(net, img, tile, pad=10):
    x = torch.from_numpy(np.asarray(img, np.float32) / 255).permute(2, 0, 1)[None]
    _, _, h, w = x.shape; out = torch.zeros(1, 3, h * 4, w * 4)
    for y0 in range(0, h, tile):
        for x0 in range(0, w, tile):
            ya, yb, xa, xb = max(0, y0 - pad), min(h, y0 + tile + pad), max(0, x0 - pad), min(w, x0 + tile + pad)
            with torch.no_grad(): o = net(x[:, :, ya:yb, xa:xb])
            ty, tx = (y0 - ya) * 4, (x0 - xa) * 4; th, tw = (min(h, y0 + tile) - y0) * 4, (min(w, x0 + tile) - x0) * 4
            out[:, :, y0 * 4:y0 * 4 + th, x0 * 4:x0 * 4 + tw] = o[:, :, ty:ty + th, tx:tx + tw]
    return Image.fromarray((out[0].clamp(0, 1).permute(1, 2, 0).numpy() * 255 + 0.5).astype(np.uint8))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("pth"); ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--model", default="compact"); ap.add_argument("--tile", type=int, default=256)
    A = ap.parse_args(); os.makedirs(A.dst, exist_ok=True); torch.set_num_threads(os.cpu_count())
    net = SRVGGNetCompact() if A.model == "compact" else RRDBNet()
    sd = torch.load(A.pth, map_location="cpu"); sd = sd.get("params_ema", sd.get("params", sd))
    net.load_state_dict(sd, strict=True); net.eval()
    fs = sorted(glob.glob(os.path.join(A.src, "*.jpg")))
    for i, f in enumerate(fs):
        o = os.path.join(A.dst, os.path.basename(f))
        if os.path.exists(o): continue
        t = time.time(); run(net, Image.open(f).convert("RGB"), A.tile).save(o, quality=95)
        print(f"{i + 1}/{len(fs)} {time.time() - t:.1f}s", flush=True)
