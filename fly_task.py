import dataclasses
import time

from pioneer_sdk.piosdk import Pioneer


@dataclasses.dataclass
class Point:
    x: float
    y: float


class FlightPlanner:

    @classmethod
    def create_snake_trajectory(cls, start_point: Point, fin_point: Point, num_x_point: int = 2, num_y_point: int = 2):
        """
        Функция для генерации списка точек в виде змейки
        :param start_point: Point(x, y)     - стартовая точка траектории
        :param fin_point: Point(x, y)       - конечная точка траектории
        :param num_x_point: int             - количество промежуточных точек вдоль оси Х
        :param num_y_point: int             - количество промежуточных точек вдоль оси У
        :return: list[Point]                - список точек для полета по траектории
        """

        trajectory = []

        dx = (fin_point.x - start_point.x) / num_x_point
        dy = (fin_point.y - start_point.y) / num_y_point

        trajectory.append(start_point)
        for x_point in range(num_x_point):
            for y_point in range(num_y_point):
                last_point = trajectory[-1]
                if x_point % 2 == 0:
                    y = last_point.y + dy
                else:
                    y = last_point.y - dy

                trajectory.append(Point(last_point.x, y))

            last_point = trajectory[-1]
            x = last_point.x + dx
            trajectory.append(Point(x, last_point.y))

        return trajectory


# Создаём траекторию змейки. Начальная и конечная точки должны быть в противоположных углах полигона.
trajectory_points = FlightPlanner.create_snake_trajectory(Point(-2, -2), Point(2, 2), 4, 4)

# Адрес для подключения
PIONEER_IP = "127.0.0.1"
PIONEER_PORT = 8000

pio = Pioneer(ip=PIONEER_IP, mavlink_port=PIONEER_PORT)

pio.arm()
pio.takeoff()

while not pio.takeoff():
    pass

pio.raspberry_start_capture()
for point in trajectory_points:
    pio.go_to_local_point(point.x, point.y, -1.8, yaw=0)

    while not pio.point_reached():
        time.sleep(0.05)

pio.raspberry_stop_capture()
pio.land()
pio.disarm()
