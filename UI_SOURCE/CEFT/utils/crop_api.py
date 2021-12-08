from pathlib import Path
from collections import namedtuple
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from PIL import Image

import shlex, subprocess
import tempfile
import logging

CropRectangle = namedtuple("CropRectangle", "left top width height")


def reservoir_sampling(stream, K=5):
    reservoir = []
    for i, item in enumerate(stream, start=1):
        if i <= K:
            reservoir.append(item)
            continue
        # Append new element with prob K/i
        sample_prob = K / i
        should_append = np.random.rand() < sample_prob
        if should_append:
            # replace random element with new element
            rand_idx = np.random.randint(K)
            reservoir[rand_idx] = item
    return reservoir


def parse_output(output):
    output = output.splitlines()
    final_output = {
        "salient_point": [],
        "crops": [],
        "all_salient_points": [],
    }
    key = "salient_point"
    for i, line in enumerate(output):
        line = line.split()
        if len(line) in {2, 4}:
            line = [int(v) for v in line]
            if i != 0:
                key = "crops"
        elif len(line) == 3:
            key = "all_salient_points"
            line = [float(v) for v in line]
        else:
            raise RuntimeError(f"Invalid line: {line}")
        final_output[key].append(line)
    return final_output


def fit_window(center: int, width: int, maxWidth: int):
    if width > maxWidth:
        raise RuntimeError("error: width cannot exceed maxWidth")

    fr: int = center - width // 2
    to: int = fr + width

    if fr < 0:
        # window too far left
        fr = 0
        to = width
    elif to > maxWidth:
        # window too far right
        to = maxWidth
        fr = to - width
    return fr, to


def generate_crop(img, x, y, targetRatio):
    (
        imageHeight,
        imageWidth,
    ) = img.shape[:2]
    imageRatio: float = (imageHeight) / imageWidth

    if targetRatio < imageRatio:
        # squeeze vertically
        window = fit_window(y, np.round(targetRatio * imageWidth), imageHeight)
        top = window[0]
        height = max(window[1] - window[0], 1)
        left = 0
        width = imageWidth
    else:
        # squeeze horizontally
        window = fit_window(x, np.round(imageHeight / targetRatio), imageWidth)
        top = 0
        height = imageHeight
        left = window[0]
        width = max(window[1] - window[0], 1)

    rect = CropRectangle(left, top, width, height)
    return rect


def is_symmetric(
    image: np.ndarray, threshold: float = 25.0, percentile: int = 95, size: int = 10
) -> bool:
    if percentile > 100:
        raise RuntimeError("error: percentile must be between 0 and 100")
        return False

    # downsample image to a very small size
    mode = None
    if image.shape[-1] == 4:
        # Image is RGBA
        mode = "RGBA"
    imageResized = np.asarray(
        Image.fromarray(image, mode=mode).resize((size, size), Image.ANTIALIAS)
    ).astype(int)
    imageResizedFlipped = np.flip(imageResized, 1)

    # calculate absolute differences between image and reflected image
    diffs = np.abs(imageResized - imageResizedFlipped).ravel()

    maxValue = diffs.max()
    minValue = diffs.min()

    # compute asymmetry score
    score: float = np.percentile(diffs, percentile)
    logging.info(f"score [{percentile}]: {score}")
    score = score / (maxValue - minValue + 10.0) * 137.0
    logging.info(f"score: {score}\tthreshold: {threshold}\t{maxValue}\t{minValue}")
    return score < threshold


class NewClass(object):
    def newFunc():
        return "Hello from NewClass"


class ImageSaliencyModel(object):
    def __init__(
        self,
        crop_binary_path,
        crop_model_path,
        aspectRatios=None,
    ):
        self.crop_binary_path = crop_binary_path
        self.crop_model_path = crop_model_path
        self.aspectRatios = aspectRatios
        self.cmd_template = (
            f'{self.crop_binary_path} {self.crop_model_path} "{{}}" show_all_points'
        )

    def get_output(self, img_path, aspectRatios=None):
        cmd = self.cmd_template.format(img_path.absolute())
        if aspectRatios is None:
            aspectRatios = self.aspectRatios
        if aspectRatios is not None:
            aspectRatio_str = " ".join(str(ar) for ar in aspectRatios)
            cmd = f"{cmd} {aspectRatio_str}"
        output = subprocess.check_output(cmd, shell=True)  # Success!
        output = parse_output(output)
        return output

    def saveHeatMap(self, img, all_salient_points, heatmap_path):
        fig, ax = plt.subplots(1, 1)
        sx, sy, sz = zip(*all_salient_points)
        ax.imshow(img, alpha=0.1)
        ax.scatter(sx, sy, c=sz, s=100, alpha=0.8, marker="s", cmap="Reds")
        ax.set_axis_off()
        fig.savefig(heatmap_path)
        return ax


    def plot_saliency_map(self, img, all_salient_points, ax = None, download = False):
        if ax is None:
            fig, ax = plt.subplots(1, 1)
        # Sort points based on Y axis
        sx, sy, sz = zip(*all_salient_points)
        ax.imshow(img, alpha=0.1)
        ax.scatter(sx, sy, c=sz, s=100, alpha=0.8, marker="s", cmap="Reds")
        # return ax
        ax.set_axis_off()
        return ax

    def plot_saliency_scores_for_index(self, img, all_salient_points, ax=None):
        if ax is None:
            fig, ax = plt.subplots(1, 1)
        # Sort points based on Y axis
        sx, sy, sz = zip(*sorted(all_salient_points, key=lambda x: (x[1], x[0])))

        ax.plot(sz, linestyle="-", color="r", marker=None, lw=1)
        ax.scatter(
            np.arange(len(sz)), sz, c=sz, s=100, alpha=0.8, marker="s", cmap="Reds"
        )
        for i in range(0, len(sx), len(set(sx))):
            ax.axvline(x=i, lw=1, color="0.1")
        ax.axhline(y=max(sz), lw=3, color="k")
        return ax

    def plot_crop_area(
        self,
        img,
        salient_x,
        salient_y,
        aspectRatio,
        ax=None,
        original_crop=None,
        checkSymmetry=True,
    ):
        if ax is None:
            fig, ax = plt.subplots(1, 1)
        ax.imshow(img)
        ax.plot([salient_x], [salient_y], "-yo", ms=20)
        ax.set_title(f"ar={aspectRatio:.2f}")
        ax.set_axis_off()

        patches = []
        if original_crop is not None:
            x, y, w, h = original_crop
            patches.append(
                Rectangle((x, y), w, h, linewidth=5, edgecolor="r", facecolor="none")
            )
            ax.add_patch(patches[-1])
            logging.info(f"ar={aspectRatio:.2f}: {((x, y, w, h))}")
        # For non top crops show the overlap of crop regions
        x, y, w, h = generate_crop(img, salient_x, salient_y, aspectRatio)
        logging.info(f"Gen: {((x, y, w, h))}")
        # print(x, y, w, h)
        patches.append(
            Rectangle((x, y), w, h, linewidth=5, edgecolor="y", facecolor="none")
        )
        ax.add_patch(patches[-1])

        if checkSymmetry and is_symmetric(img):
            x, y, w, h = generate_crop(img, img.shape[1], salient_y, aspectRatio)
            logging.info(f"Gen: {((x, y, w, h))}")
            # print(x, y, w, h)
            patches.append(
                Rectangle((x, y), w, h, linewidth=5, edgecolor="b", facecolor="none")
            )
            ax.add_patch(patches[-1])

        return ax

    def plot_img_top_crops(self, img_path):
        return self.plot_img_crops(img_path, topK=1, aspectRatios=None)

    def someNewFunction():
        print("CALLED: someNewFunction")
        return "Hello"

    def plot_img_crops(
        self,
        img_path,
        heatmap_path,
        topK=1,
        aspectRatios=None,
        checkSymmetry=True,
        sample=False,
        col_wrap=None,
        add_saliency_line=True,
    ):
        print("2. HELLO, starting plot_img_crops")
        img = mpimg.imread(img_path)
        img_h, img_w = img.shape[:2]

        if aspectRatios is None:
            aspectRatios = self.aspectRatios

        if aspectRatios is None:
            print("No aspects passed. Taking default ones.")
            aspectRatios = [0.3125, 0.625, 1.0, 1.14, 2]

        print("Aspects being submitted: ", aspectRatios)
        output = self.get_output(img_path, aspectRatios=aspectRatios)
        n_crops = len(output["crops"])
        salient_x, salient_y, = output[
            "salient_point"
        ][0]
        # img_w, img_h = img.shape[:2]

        logging.info(f"{(img_w, img_h)}, {aspectRatios}, {(salient_x, salient_y)}")

        if img_w > img_h:
            fig_w = 5
            fig_h = fig_w * (img_h / img_w)
        else:
            fig_h = 5
            fig_w = fig_h * (img_w / img_h)
        per_K_rows = 1
        if n_crops == 1:
            nrows = n_crops + add_saliency_line
            ncols = topK + 1
            fig_width = fig_w * ncols
            fig_height = fig_h * nrows
        else:
            nrows = topK + add_saliency_line
            ncols = n_crops + 1
            fig_width = fig_w * ncols
            fig_height = fig_h * nrows

            if col_wrap:
                per_K_rows = int(np.ceil((n_crops + 1) / col_wrap))
                nrows = topK * per_K_rows + add_saliency_line
                ncols = col_wrap
                fig_width = fig_w * ncols
                fig_height = fig_h * nrows


        # print("->", nrows, ncols)


        # Sort based on saliency score
        all_salient_points = output["all_salient_points"]
        sx, sy, sz = zip(*sorted(all_salient_points, key=lambda x: x[-1], reverse=True))
        A2 = [ _ for _ in all_salient_points ]
        A2.sort(key = lambda x: x[-1], reverse=True)
        # print(A2)

        ax_map = self.saveHeatMap(img, all_salient_points, heatmap_path)

        fig = plt.figure(constrained_layout=False, figsize=(fig_width, fig_height))
        gs = fig.add_gridspec(nrows, ncols)
        plt.title("Crops for different aspect ratios", y=1.08, fontdict = {'fontsize' : 27}, color = 'r')
        # plt.show()

        sx = np.asarray(sx)
        sy = np.asarray(sy)
        sz = np.asarray(sz) 

        avg_x, avg_y = 0, 0
        for i in range(10):
            avg_x += sx[i]
            avg_y += sy[i] 
        avg_x /= 10
        avg_y /= 10

        for t in range(0, topK):
            salient_x, salient_y, saliency_score = sx[t], sy[t], sz[t]
            logging.info(f"t={t}: {(salient_x, salient_y, saliency_score)}")
            # print(f"t={t}: {(salient_x, salient_y, saliency_score)}")
            if n_crops > 1 or (t == 0 and n_crops == 1):
                ax_map = fig.add_subplot(gs[t * per_K_rows, 0])
                ax_map = self.plot_saliency_map(img, all_salient_points, ax=ax_map)

            extent = ax_map.get_window_extent().transformed(fig.dpi_scale_trans.inverted())

            for i, original_crop in enumerate(output["crops"]):
                if n_crops == 1:
                    ax = fig.add_subplot(gs[i, t + 1], sharex=ax_map, sharey=ax_map)
                else:
                    ax = fig.add_subplot(
                        gs[t * per_K_rows + ((i + 1) // ncols), (i + 1) % (ncols)],
                        sharex=ax_map,
                        sharey=ax_map,
                    )
                aspectRatio = aspectRatios[i]
                self.plot_crop_area(
                    img,
                    salient_x,
                    salient_y,
                    aspectRatio,
                    ax=ax,
                    original_crop=original_crop,
                    checkSymmetry=checkSymmetry,
                )
                if n_crops == 1:
                    ax.set_title(f"Saliency Rank: {t+1} | {ax.get_title()}")
        if add_saliency_line:
            ax = fig.add_subplot(gs[-1, :])
            self.plot_saliency_scores_for_index(img, all_salient_points, ax=ax)
        fig.tight_layout()
        return {
            "image_size": (img_w, img_h),
            "salient_coordinates": (salient_x, salient_y),
            "top10_average_coordinates": (avg_x, avg_y)
        }

    def plot_img_crops_using_img(
        self,
        img,
        img_format="JPEG",
        **kwargs,
    ):
        with tempfile.NamedTemporaryFile("w+b") as fp:
            print(fp.name)
            img.save(fp, img_format)
            self.plot_img_crops(Path(fp.name), **kwargs)
