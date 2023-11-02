import math
import cv2
import numpy as np

# Читаем картинки
img1 = cv2.imread('images/panda.jpg', 0)
img2 = cv2.imread('images/panda_rot.jpg', 0)


class Solution:
    """
    Класс решения.
    """
    @staticmethod
    def find_similarity(im1: np.ndarray, im2: np.ndarray) -> float:
        """
        Ищет похожесть между двумя картинками.
        :param im1: Первая картинка
        :param im2: Вторая картинка
        :return: Похожесть двух картинок (меньше -> больше похожесть)
        """

        # Считаем гистограммы картинок
        hist1 = cv2.calcHist(im1, [0], None, [256], [0, 256])
        hist2 = cv2.calcHist(im2, [0], None, [256], [0, 256])

        # Сравниваем гистограммы
        return cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)

    @staticmethod
    def find_rotation_cv(im1: np.ndarray, im2) -> float:
        """
        Ищет угол поворота картинки в градусах
        :param im1: Первая картинка
        :param im2: Вторая картинка (повёрнутая первая)
        :return: Угол поворота картинки в градусах
        """
        # Будем сравнивать картинки по методу SIFT
        orb = cv2.SIFT_create()

        kp1, des1 = orb.detectAndCompute(im1, None)
        kp2, des2 = orb.detectAndCompute(im2, None)

        index_params = dict(algorithm=2, trees=5)
        search_params = dict(checks=50)

        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(des1, des2, k=2)

        goods = []
        for m, n in matches:
            if len(goods) > 20:
                break

            if m.distance < 0.7 * n.distance:
                goods.append(m)

        src_pts = np.float32([kp1[m.queryIdx].pt for m in goods]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[n.trainIdx].pt for n in goods]).reshape(-1, 1, 2)

        # Составляем гомограф-матрицу
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        # Считаем угол в градусах по гомограф-матрице
        return - math.atan2(M[0, 1], M[0, 0]) * 180 / math.pi


print(Solution.find_similarity(img1, img2))
print(Solution.find_rotation_cv(img1, img2))
