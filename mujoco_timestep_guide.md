# MuJoCo Physics Timestep Guide

## 🔬 Physics Timestep Nedir?

**Timestep**, MuJoCo'nun fizik simülasyonunu ne sıklıkta hesapladığını belirleyen temel parametredir. Daha küçük timestep = daha hassas fizik, daha büyük timestep = daha hızlı simülasyon.

## ⚖️ Timestep Değerleri ve Etkileri

### 🐌 Küçük Timestep (Yüksek Hassasiyet)
```python
timestep = 0.0001  # 0.1ms - Ultra hassas
timestep = 0.0005  # 0.5ms - Çok hassas  
timestep = 0.001   # 1ms - Hassas
```

**Avantajlar:**
- ✅ Çok hassas fizik hesaplamaları
- ✅ Kararlı simülasyon (stable)
- ✅ Gerçekçi temas dinamikleri
- ✅ Hassas robot kontrolü

**Dezavantajlar:**
- ❌ Çok yavaş simülasyon
- ❌ Yüksek CPU kullanımı
- ❌ GPU üzerinde fazla yük

### ⚡ Büyük Timestep (Yüksek Hız)
```python
timestep = 0.01    # 10ms - Hızlı
timestep = 0.02    # 20ms - Çok hızlı
timestep = 0.05    # 50ms - Ultra hızlı
```

**Avantajlar:**
- ✅ Çok hızlı simülasyon
- ✅ Düşük CPU kullanımı
- ✅ Real-time'dan daha hızlı

**Dezavantajlar:**
- ❌ Fizik hassasiyeti düşük
- ❌ Simülasyon kararsızlığı
- ❌ Gerçekçi olmayan davranışlar

## 🎯 Optimal Timestep Seçimi

### 🤖 Robot Simülasyonu İçin
```python
# Genel robotik uygulamalar
timestep = 0.002   # 2ms - İyi denge

# SLAM/Navigation
timestep = 0.005   # 5ms - Hız-hassasiyet dengesi

# Manipülasyon/Grasping
timestep = 0.001   # 1ms - Yüksek hassasiyet gerekli
```

### 🎮 Performans Odaklı
```python
# Maximum GPU kullanımı için
timestep = 0.0005  # 0.5ms - GPU'yu zorlar
nsubsteps = 16     # Çok fazla hesaplama
```

## 🔧 Substeps (Alt Adımlar)

**Substeps**, her timestep içinde kaç kez fizik hesaplaması yapılacağını belirler:

```python
timestep = 0.002
nsubsteps = 4      # Total: 0.002/4 = 0.0005s effective timestep
```

### Substep Hesaplama:
- **Effective Timestep** = `timestep / nsubsteps`
- **Daha fazla substep** = Daha hassas fizik + Daha yavaş simülasyon

## 📊 Projekteki Mevcut Ayarlar

### Stretch SLAM Bridge'deki Ayarlar:
```python
# stretch_slam_bridge_improved.py içinde
performance_opts = {
    'physics_substeps': 12,     # 12 alt adım
    'solver_iterations': 150,   # 150 çözücü iterasyonu
}
```

### Extreme GPU Config:
```python
# extreme_gpu_config.py içinde
'timestep': 0.0005,        # 0.5ms - Çok hassas
'nsubsteps': 16,           # 16 alt adım
'iterations': 200,         # 200 solver iterasyonu
```

## ⏱️ Timestep vs Performance

| Timestep | Substeps | Effective | Performance | GPU Load | Use Case |
|----------|----------|-----------|-------------|----------|----------|
| 0.02     | 1        | 0.02s     | 🚀🚀🚀🚀🚀      | 🔋        | Demo/Prototype |
| 0.005    | 2        | 0.0025s   | 🚀🚀🚀🚀        | 🔋🔋      | SLAM/Navigation |
| 0.002    | 4        | 0.0005s   | 🚀🚀🚀         | 🔋🔋🔋    | Robotics Standard |
| 0.001    | 8        | 0.000125s | 🚀🚀           | 🔋🔋🔋🔋  | High Precision |
| 0.0005   | 16       | 0.00003s  | 🚀             | 🔋🔋🔋🔋🔋 | Ultra Precision |

## 🎛️ Dinamik Timestep Ayarlama

### Kod Örneği:
```python
def set_timestep_for_task(task_type):
    if task_type == "navigation":
        return {'timestep': 0.005, 'nsubsteps': 2}
    elif task_type == "manipulation": 
        return {'timestep': 0.001, 'nsubsteps': 8}
    elif task_type == "gpu_stress":
        return {'timestep': 0.0005, 'nsubsteps': 16}
    else:
        return {'timestep': 0.002, 'nsubsteps': 4}  # Default
```

## 🔍 Timestep Monitoring

### Performance İzleme:
```python
# Gerçek zamanlı oran kontrolü
real_time_ratio = simulation_time / wall_clock_time

if real_time_ratio < 0.5:  # Çok yavaş
    # Timestep'i artır veya substeps'i azalt
    timestep *= 1.5
elif real_time_ratio > 2.0:  # Çok hızlı
    # Timestep'i azalt veya substeps'i artır  
    timestep *= 0.8
```

## 💡 Öneriler

### GPU Kullanımını Artırmak İçin:
1. **Küçük timestep kullan** (0.0005-0.001)
2. **Substeps'i artır** (12-20)
3. **Solver iterations'ı artır** (150-300)
4. **Contact detection'ı yükselt**

### Simülasyon Hızını Artırmak İçin:
1. **Büyük timestep kullan** (0.005-0.01)
2. **Substeps'i azalt** (1-4)  
3. **Solver iterations'ı azalt** (20-50)
4. **Basit contact models kullan**

### Hassasiyet İçin:
1. **Çok küçük timestep** (0.0001-0.0005)
2. **Çok fazla substep** (20-50)
3. **Yüksek solver tolerance** (1e-10)
4. **Dense Jacobian matrices**

## 🎯 Sonuç

**Timestep seçimi**, simülasyonun kalitesi ve hızı arasındaki dengeyi belirler. GPU performansını maksimize etmek için küçük timestep + fazla substeps kullanın, hız için büyük timestep + az substeps tercih edin.

**Projektede mevcut ayarlar** maksimum GPU kullanımı için optimize edilmiştir!