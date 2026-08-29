---
title: "van_den_Ende DDCN 笔记"
date: 2026-08-26T19:48:02+08:00
draft: false
slug: 
categories: [DAS,AI,笔记]
---
# 项目地址

**对应论文**

Deep Deconvolution for Traffic Analysis With Distributed Acoustic Sensing Data

**文件地址**

D:\study\graduate\code\python\van-den-Ende-DDCN

**doi地址**

https://ieeexplore.ieee.org/document/9966323/

https://doi.org/10.1109/TITS.2022.3223084

**数据与代码仓库地址**

[doi.org/10.6084/m9.figshare.16653163](doi.org/10.6084/m9.figshare.16653163.)    * 用的这个

https://github.com/Juanx65/DeepDeconvV2.git

---

# 项目结构

- 绘图jupyter notebook

- 模型
- 数据
- 波束成形和对比算法

## 原理

1. 认为车致信号为脉冲信号，与信道产生卷积
2. 通过UNet恢复稀疏信号X，波束成形 + Music 滤波
3. 稀疏信号X与固定的冲激函数进行反卷积，恢复车辆信号
4. 损失函数 = MSE + X的L1正则

## 1. 这个仓库是什么

  这是 van den Ende 等人 DAS 交通监测论文的代码（仓库名 van-den-Ende-DDCN）。DAS = 分布式光纤声学传感：埋在路边的光纤记
  录车辆经过时的应变率信号。论文的核心问题是稀疏反卷积（Deep Deconvolution）：光纤记录到的是“车辆脉冲序列 × 光纤冲激响应

  + **训练一个 UNet 把观测信号还原成稀疏脉冲，再做波束形成估计车速、恢复车辆轨迹。**

## 2. 项目结构

  - models.py — 核心：UNet/ResNet 反卷积模型、DataGenerator 数据增强、CallBacks 回调
  - beamforming.py — 多锥度（multitaper）协方差估计 + MUSIC/常规波束形成，在慢度网格上扫描
  - ISTA.py — 经典稀疏反卷积基线：FISTA 迭代软阈值（JAX 实现）
  - utils.py — FFT_roll（慢度时移对齐）、peak_projection（峰值检测）、match_peaks（与人工拾取匹配评估）
  - Fig*.ipynb — 论文全部插图，同时是使用示例：Fig2_impulse_response（冲激响应）、Fig4_architecture（网络结构）、
    FigS1_training_curves（训练曲线）、Fig10/11、Figs6-9（评估）

  - requirements.txt — numpy/scipy/tensorflow>=2.3/jax/numba/spectrum/h5py 等
  - data.tar\data\ — 实际数据目录：DAS_data.h5（1.6 GB 主记录）、kernel.npy（冲激响应）、saved-model.h5（预训练权重）、
    multicars_extract.npy、picks_forward/backward.npy（人工拾取的车辆轨迹）、coords_Teil.npy（光纤几何坐标）、logs/（训
    练 TensorBoard 日志）

  ## 3. 核心模型与训练方法

  观测模型：y = h ⊛ x + n，其中 h 是已知的冲激响应（kernel.npy，实测自单辆车经过）。

  - 网络前向（models.py:280）：UNet 输出稀疏脉冲图 x_hat，再用固定卷积 h 得到重建观测 y_hat。训练时只有 y_hat 参与监督，
    这就是“物理约束自监督”反卷积。**（意思是：UNet 输出稀疏信息 x_hat，也就是车致信号，通过固定卷积 h 得到 y_hat; 训练时只有 y_hat 参与监督意思是 损失函数计算 y_hat 和 y）**
  - 损失（models.py:290）：total = ‖y − y_hat‖² + λ·‖x_hat‖₁，即拟合项 + 稀疏项。论文里 λ = 10（代码中叫 rho/lam），训练
    曲线按 rho·l1 绘制以体现贡献占比。**（正则化）**
  - 结构：kernel=(3,5)、激活 swish、正交初始化、Adam lr=5e-4；推理用配置 f0=8, blocks=3, AA=False, bn=False,
    dropout=1.0（dropout 实际是 GaussianNoise，见 models.py:356）。下采样用 MaxBlurPool（抗混叠），上采样双线性 + skip
    连接，最后 relu 输出保证非负脉冲。
  - 数据：DataGenerator（models.py:17）从长记录里随机截 win 宽窗口，并做时间/通道翻转增强；每个 epoch 重新采样。
  - 训练流程：约 1000 epoch，ModelCheckpoint 按 val_loss 保存最佳权重 → saved-model.h5，TensorBoard 记录 loss/l2/l1（见
    FigS1_training_curves 与 logs/）。

---

# 我的理解（修正版）

```
y (观测) → UNet → x_hat (稀疏脉冲图)
                   │
                   ├─ 与已知冲激响应 h 卷积 → y_hat (重建观测)
                   │     损失 = MSE(y, y_hat) + λ·‖x_hat‖₁
                   │
                   └─ 推理时只取 x_hat → FFT_roll 慢度对齐 → 波束形成扫描 → 轨迹
```

三处小修正：
- UNet 输出在代码里叫 `x_hat`。
- **L1 正则加在输出信号 `x_hat` 上，不是网络权重上**——它不是“参数稀疏化”，而是物理先验“车辆事件在时空上是稀疏的”。模型学的是“去卷积”，因为只有把脉冲放在车辆事件位置，`h⊛x̂` 才能匹配 `y`。
- **波束形成是对 `x_hat` 做的**，不是 `y_hat`。`Fig10` cell 10 把 UNet 输出 `x` 存入 `"deep"` 类别，之后才做 `FFT_roll` + `Beamformer`。

## Q1：你的数据是 1000 Hz

采样率会影响三处，都需要对齐：

- **时间窗**：模型推理用 `win=1024`，50 Hz 时是 20.5 s，足够覆盖一次完整过车（24 通道 × 3.2 m ≈ 77 m，80 km/h 约 3.5 s）。
- **冲激响应 `h`**：`kernel.npy` 有 866 个采样点，50/80 Hz 下约 10–17 s 的物理响应。**【可以改进的地方：将冲激响应换成自己建模的冲激响应。】**
- **波束形成频带**：论文用 `(0.5, 2.0) Hz` 频段，车辆 DAS 信号能量集中在这附近；1000 Hz 的奈奎斯特频段大部分是噪声。

**建议：低通滤波 + 降采样到 50–100 Hz**，例如 `scipy.signal.decimate(x, 10)`（先滤后抽，避免混叠）。这样 `win=1024` 对应 10–20 s，论文的模型和 pipeline 几乎原样可用。坚持 1000 Hz 需要把窗口放到 ~20000 点、kernel 重采样到 ~17000 点，卷积成本高且没有信息增益。

另外两点：模型输入是 24 通道（`data_shape=(24, 1024, 1)`）【24是所有的通道数量】，你的光纤通道数不同需要按自己的 `Nch` 重训；`gauge=3.2 m` 是他们的道间距，也要换成你自己的。`3.2*24=76.8`m.

## Q2：需要人工标注轨迹吗？

**训练不需要。** 这个方法是自监督/物理约束的：只需要原始 DAS 记录 `y` 和已知的 `h`，损失在观测域比较 `y` 与 `h⊛x̂`，全程没有标签参与。

`picks_forward.npy` / `picks_backward.npy`（人工拾取的车辆轨迹）**只用于评估**：`Fig10/11` 里用 `match_peaks` 把算法检测结果和人工拾取对比，画 ROC 和检测统计。

---

# 复现代码仓库

**激活环境**

```cmd
# conda 新环境
conda create -n tf python=3.10 -y
conda activate tf
  
# 安装库
pip list
pip install tensorflow==2.10.0 numpy==1.25.3 scipy jax h5py matplotlib seaborn numba spectrum notebook ipympl	
```

`requirements.txt`

```txt
numpy					# 
scipy					
tensorflow==2.10.0		# 
jax						# 
numba
spectrum
seaborn
matplotlib
ipympl
cartopy
osmnx
h5py
notebook
```

**目录链接**

Notebook 写死数据放在 .\data , 实际数据放在 .\data.tar\data

不建议用目录链接（永久保存在 NTFS 磁盘，重启不掉），实际做法把data.tar文件夹改名

```powershell
New-Item -ItemType Junction -Path .\data -Target .\data.tar\data
```

**跑通模型**

Fig10_performance_statistics.ipynb

---

# **Q&A**

> ModuleNotFoundError: No module named 'beamforming'
>
> jupyter notebook 报错，实际上 beamforming.py 与 ipynb 文件在同一目录下，我在 vscode 中运行 notebook，如何解决

```python
import os
import sys

# 将当前 Notebook 所在目录加入搜索路径
sys.path.append("D:\\study\\graduate\\code\\python\\van-den-Ende-DDCN")
```

```python
# 带来的附属问题，jupyter notebook 当前目录是 jupyter notebook 命令启动目录
# FileNotFoundError: [Errno 2] Unable to synchronously open file (unable to open file: name = 'C:\Users\72950\data\DAS_data.h5')

# r"" 原始字符串，直接写单反斜杠
os.chdir(r"D:\study\graduate\code\python\van-den-Ende-DDCN")

# 获取当前工作目录绝对路径，加入模块搜索路径
current_dir = os.path.abspath(".")
sys.path.append(current_dir)
```

---

> numpy 版本过高，如何降级？

```python
pip install "numpy<1.24.0" --force-reinstall
# 或者直接指定推荐版本：
pip install numpy==1.23.5
```

---

> tensorflow 和 numpy 版本不冲突，但是其他包可能导致 numpy 版本冲突而报错

```markdown
codex: 已解决，tf（tensorflow）环境的依赖冲突处理完成。做了什么

  - 定位冲突根源：tensorflow 2.10.0 要求 numpy 1.23.x，而 jax 0.6.2/jaxlib 0.6.2（需 numpy≥1.26）和 ml-dtypes 0.6.0（需 numpy≥2.0）把环境搞冲突，甚至导致 import tensorflow 直接报错。

  - 已卸载 jax、jaxlib、ml-dtypes（环境内无其他包依赖它们）。
```

---

> 兼容的版本 `requirements.txt`

```txt
# Verified combo on Windows (Python 3.10, conda env: tf)
# jax 0.4.30 is the newest version still compatible with numpy 1.23.x
# (jax 0.4.31+ requires numpy>=1.24; ml-dtypes 0.6.0 requires numpy>=2.0).
# tensorflow 2.10 breaks with numpy>=1.24 (np.bool removal), so keep numpy==1.23.5.
numpy==1.23.5
tensorflow==2.10.0
jax==0.4.30
jaxlib==0.4.30
ml-dtypes==0.4.1
scipy==1.15.3
```

```powershell
# 查看某包的版本
pip show <包名>
# 或
conda list <包名>
```

---

# 模型结构

`models.py`

**结构**

```python
class DataGenerator(keras.utils.Sequence):
    # 相当于 pytorch 的data_loader
    ...

# 定义了回调方法，分别记录日志、保存最佳模型
class CallBacks:
    @staticmethod
    def tensorboard(logdir):
        tensorboard_callback = keras.callbacks.TensorBoard(
            ...
        )
        return tensorboard_callback

    @staticmethod
    def checkpoint(savefile):
        checkpoint_callback = keras.callbacks.ModelCheckpoint(
            ...
        )
        return checkpoint_callback

# 模型
class ResNet(keras.Model):

    def __init__(self, impulse_response, lam=0.0, f0=4, data_shape=(24, 1024, 1), blocks=4, AA=True, bn=False, dropout=0.0):
        super().__init__()
        # 初始化模型，指定参数
        pass
    
    # 前向过程
    def call(self, x):
        x_hat = self.ResNet(x)
        y_hat = tf.nn.conv2d(x_hat, self.impulse_response, padding="SAME", strides=1)
        return x_hat, y_hat
    
    # 重写 compile()
    def compile(self, opt):
        super().compile()
        self.opt = opt						# 指定 optimizer 
        pass
    
    # 计算损失函数
    def compute_loss(self, Y, Y_hat, X):
        l1 = tf.reduce_mean(tf.abs(X))
        l2 = tf.reduce_mean(tf.square(Y - Y_hat))
        total_loss = l2 + self.lam * l1
        return total_loss, l2, l1
    
    # 正向传播：X, Y_hat = self.call(Y) (对应 PyTorch 里的 output = model(data))
	# 计算损失：total_loss, ... = self.compute_loss(...) (对应 loss = criterion(...))
	# 反向传播求梯度：grads = tape.gradient(total_loss, RN_vars) (对应 loss.backward())
	# 更新权重：self.opt.apply_gradients(zip(grads, RN_vars))
    def train_step(self, Y):
        if isinstance(data, tuple):
            Y = Y[0]
            
        RN = self.ResNet
        RN_vars = RN.trainable_variables
        
        with tf.GradientTape() as tape:
            X, Y_hat = self.call(Y)
            total_loss, l2_loss, l1_loss = self.compute_loss(Y, Y_hat, X)
            
        grads = tape.gradient(total_loss, RN_vars)
        
        self.opt.apply_gradients(zip(grads, RN_vars))
        self.compiled_metrics.update_state(Y, Y_hat)
        return {
            "loss": total_loss,
            "l2": l2_loss,
            "l1": l1_loss,
        }
    
    def test_step(self, Y):
        if isinstance(data, tuple):
            Y = Y[0]
            
        X, Y_hat = self.call(Y)
        total_loss, l2_loss, l1_loss = self.compute_loss(Y, Y_hat, X)
        self.compiled_metrics.update_state(Y, Y_hat)
        return {
            "loss": total_loss,
            "l2": l2_loss,
            "l1": l1_loss,
        }

    # 模块
    def conv_layer(self, x, filters, kernel_size, dilation,
                   use_bn=False, use_dropout=False, use_bias=True, activ=None):
        """
        Convolution layer > batch normalisation > activation > dropout
        """
        
        return x
    
    # 模块
    def residual_block(self, x, f0):
        ...
        return x0 + x
        
	# 拼接卷积层和
    def construct(self):
        """
        Construct ResNet model
        """
        self.ResNet = Model(inputs, x)
        return self.ResNet
    
# 模型
class UNet(keras.Model):
    # 同上
```

**前向过程和损失函数**

```python
def call(self, x):
    x_hat = self.ResNet(x) 			# 神经网络预测源信号 X
    # 将预测结果与已知的物理脉冲响应进行卷积，得到重建信号
    y_hat = tf.nn.conv2d(x_hat, self.impulse_response, padding="SAME", strides=1) 
    return x_hat, y_hat

def compute_loss(self, Y, Y_hat, X):
    l1 = tf.reduce_mean(tf.abs(X)) 				# 强制预测信号稀疏 (大部分为0)
    l2 = tf.reduce_mean(tf.square(Y - Y_hat)) 	# 保证重建信号与原观测信号一致
    total_loss = l2 + self.lam * l1
    return total_loss, l2, l1
```

**`ResNet` 和 `UNet`** 

在这个代码中，`ResNet` 和 `UNet` 是**分别使用的**

---

# **代码阅读**

`Beamforming.py`

 **它的数据流**

 `输入阵列时间序列数据 X` -> `多窗频域变换 (CMTM)` -> `并行计算通道间的协方差矩阵 (Cxy)` -> `结合空间物理模型 (dt -> A)` -> `使用 MUSIC 或 传统 Beamforming 算法寻找信号到达方向`。

**CMTM多窗频域变换**

标准的 FFT 会产生频谱泄漏和高方差，先用多个正交的 Slepian 窗对信号进行加窗处理，再对多个加窗后的频谱求平均，得到稳定、低方差的协方差矩阵，这对于嘈杂信号（如脑电波、微弱地震波）极其重要。

**多窗法计算协方差矩阵**

**MUSIC算法**

**一维信号 `MUSIC` 算法**

一维时序信号的 MUSIC 算法估计的是：信号中包含的“频率成分“

```markdown
求一维信号的协方差矩阵————滑动窗口延时构建矩阵
矩阵求自相关————得到协方差矩阵，怎么求的？
正交分解，按特征值大小分为信号空间和噪声空间
通过信号空间与噪声空间正交，确定特征值和特征向量
噪声空间对应特征值置为0，再恢复信号

```

> 一维阵列采集的二维信号怎么计算协方差矩阵？

```markdown
频域法
转为频域  >>  多次快拍(多个短窗口)的频域平均  >> 求外积并平均
```

**求外积并平均**：在特定频率 f 下，空间协方差矩阵是这样算出来的：
$$
R_{xx}(f)=\frac{1}{K}\sum_{k=1}^{K} X_k(f)\,X_k(f)^H
$$

- Xk(f) 是一个列向量 (M×1)。


-   Xk(f)H 是一个行向量 (1×M)。
-   它们相乘（外积）恰好得到一个 M×M 的复数矩阵。
-   把 K 个短窗口算出来的矩阵加起来求平均。

**信号到达方向**

MUSIC 或 传统 Beamforming 算法寻找信号到达方向（信号到达方向对应车辆速度）

对一维阵列，根据阵列传感器的间距和角度关系，计算对应的延时量，截取多个快拍，从而计算二维信号的协方差矩阵

**结合空间物理模型**

`结合空间物理模型 (dt -> A)` 就是依据车辆的速度范围，限制搜索的慢度区间

