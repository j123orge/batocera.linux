# Porting Plan: rk3326-m9 Target for Batocera.linux

## Source Analysis Date: 2026-09-07
## Based on: batocera.linux repository (master branch, commit 92b00e3)

---

## 0. CRITICAL UNKNOWN: M9 Hardware Files

**The repository contains NO files referencing "M9" or "m9"** (verified via `find` and `grep` across the entire tree). The user states "os arquivos de hardware do M9 fornecidos" (M9 hardware files provided), but these files are **not present** in the checked-out repository.

**Implication**: Every subsystem analysis below is structured as:
- **Reuse from R36S**: What is known to be identical/shared based on RK3326 SoC commonality
- **Replace from R36S**: What differs based on R36S-specific hardware
- **Create new**: What must be authored based on M9-specific hardware specs (which are absent)

**The M9 hardware specification files must be provided before any code changes can be made.** The plan below identifies exactly what information is needed for each subsystem.

---

## 1. DISPLAY

### 1.1 Panel

| Aspect | R36S (known) | M9 (unknown) | Action |
|--------|-------------|-------------|--------|
| Panel type | 3.5" IPS, 640×480 | ??? | **REQUIRES M9 spec** |
| Interface | MIPI DSI 2-lane | ??? | **REQUIRES M9 spec** |
| Panel controller | ST7703 / newvision-nv3051d (varies by hardware revision) | ??? | **REQUIRES M9 spec** |
| Resolution | 640×480 (4:3) | ??? | **REQUIRES M9 spec** |
| DTSI inclusion | `rk3326.dtsi` + `rk3326-linux.dtsi` | ??? | **REQUIRES M9 spec** |

**Evidence**: The R36S uses `board/batocera/rockchip/rk3326/r36s/overlays/` with multiple panel DTBO files (`mipi-panel.dtbo.r36s-panel1` through `mipi-panel.dtbo.r36s-panel4`) supporting different panel variants. The kernel patch `002-panel-updates.patch` modifies panel drivers for `panel-newvision-nv3051d.c` and `panel-sitronix-st7703.c`. The `007-ogs-panel-timings.patch` modifies `panel-sitronix-st7701.c` timing parameters.

**Decision**: If M9 uses the same physical panel as R36S, the DTSI and overlay files are reusable. If it uses a different panel (different size, resolution, interface, or controller), a new DTS file and panel driver patches are required.

### 1.2 Display Backend

| Aspect | R36S | M9 | Action |
|--------|------|-----|--------|
| Compositor | LabWC (Wayland) | Likely LabWC | **REUSE** |
| GPU Driver | Panfrost (Mesa) | Panfrost (Mesa) | **REUSE** |
| DRM/KMS | Rockchip DRM | Rockchip DRM | **REUSE** |
| GPU | Mali-G31 MP2 | Mali-G31 MP2 (RK3326) | **REUSE** |

**Evidence**: `configs/batocera-rk3326.board` enables `BR2_PACKAGE_BATOCERA_PANFROST_MESA3D=y` and `BR2_PACKAGE_BATOCERA_WAYLAND_LABWC=y`. The kernel config includes `CONFIG_ROCKCHIP_PHY=y` and Rockchip DRM drivers. The RK3326 SoC always has Mali-G31 MP2.

**Decision**: Display backend (Panfrost + LabWC) is fully reusable. Only the panel-specific DTS/overlay configuration may differ.

---

## 2. GPU

| Aspect | R36S | M9 | Action |
|--------|------|-----|--------|
| GPU | Mali-G31 MP2 | Mali-G31 MP2 (RK3326) | **REUSE** |
| GLES version | GLES 3.2 | GLES 3.2 | **REUSE** |
| GPU OPP table | `gpu_opp_table` in DTS (560-1008MHz) | Same RK3326 OPPs | **REUSE** |
| Power model | `arm,mali-g31-power-model` | Same | **REUSE** |
| Thermal | `gpu-thermal` zone | Same | **REUSE** |
| VPU | RK3326 VPU (H.264/H.265 decode) | Same | **REUSE** |

**Evidence**: `board/batocera/rockchip/rk3326/linux_patches/001-rk3326-dts.patch` configures the GPU OPP table, power model, and thermal zone. The RK3326 datasheet confirms Mali-G31 MP2 with VPU support. `Config.in` selects `BR2_PACKAGE_BATOCERA_TARGET_ROCKCHIP_GLES3` for RK3326.

**Decision**: GPU subsystem is 100% reusable. No M9-specific GPU changes expected.

---

## 3. JOYPAD / INPUT

### 3.1 Joypad Driver

| Aspect | R36S | M9 | Action |
|--------|------|-----|--------|
| Driver architecture | `rocknix-joypad` / `retrogame_joypad_s2_f1` | ??? | **REQUIRES M9 spec** |
| ADC-based input | Yes (adc-keys + rocknix-joypad) | ??? | **REQUIRES M9 spec** |
| DTSI skeleton | `retrogame_joypad_s2_f1.dtsi` | ??? | **REQUIRES M9 spec** |
| Button mapping | D-pad, ABXY, L/R triggers, SELECT, START, MODE | ??? | **REQUIRES M9 spec** |
| Analog sticks | 2x analog sticks | ??? | **REQUIRES M9 spec** |
| Rumble | PWM-controlled via `joypad` node | ??? | **REQUIRES M9 spec** |

**Evidence**: `board/batocera/rockchip/rk3326/linux_patches/1002-input-add-input-polldev-driver.patch` adds `input-polldev` driver. `1006-stable-rocknix-joypad-dtsi.patch` creates `retrogame_joypad_s2_f1.dtsi` skeleton with 2 sticks, D-pad, ABXY, TL/TR, SELECT, START, MODE buttons. `100-fix-rg351-controllers.patch` modifies the joypad node with PWM rumble. `1003-pwm-add-pwm_set_period.patch` adds `pwm_set_period` helper. `1004-input-adc-keys-redirect-keycode-316-to-rocknix-joypa.patch` redirects keycode 316 to rocknix-joypad. `004-input-drivers.patch` adds `JOYSTICK_*` Kconfig entries for various devices.

**Decision**: The joypad driver architecture (adc-keys → rocknix-joypad → input-polldev) is reusable. However, the DTSI node properties (button layout, ADC channels, PWM pin assignments, stick configurations) MUST be replaced/created based on M9 hardware. The R36S-specific `retrogame_joypad_s2_f1.dtsi` may need to be duplicated or modified.

### 3.2 Button Layout

| Aspect | R36S | M9 | Action |
|--------|------|-----|--------|
| D-pad | GPIO-based | ??? | **REQUIRES M9 spec** |
| Face buttons | GPIO-based (BTN_EAST/SOUTH/NORTH/WEST) | ??? | **REQUIRES M9 spec** |
| Triggers | L1/L2/R1/R2 (BTN_TL/TR/TL2/TR2) | ??? | **REQUIRES M9 spec** |
| Select/Start | GPIO-based | ??? | **REQUIRES M9 spec** |
| MODE/Home | GPIO-based (BTN_MODE) | ??? | **REQUIRES M9 spec** |
| Volume buttons | GPIO keys (KEY_VOLUMEUP/DOWN) | ??? | **REQUIRES M9 spec** |

**Evidence**: `005-unigue-gpio-guid.patch` changes GPIO key product/version IDs. The R36S `boot.ini` and DTS files define GPIO button mappings. The `fsoverlay/etc/init.d/S32colorbuttonled` script controls LED colors.

---

## 4. AUDIO

| Aspect | R36S | M9 | Action |
|--------|------|-----|--------|
| Audio codec | RK3326 internal I2S/PCM | RK3326 internal I2S/PCM | **REUSE** |
| Speakers | Stereo (RK3326 built-in) | ??? | **REQUIRES M9 spec** |
| Headphone jack | 3.5mm (analog) | ??? | **REQUIRES M9 spec** |
| Audio driver | ASoC Rockchip | ASoC Rockchip | **REUSE** |
| UCM configuration | `alsa-ucm-conf` patches | Same framework | **REUSE** |
| Bluetooth audio | BT ALSA | BT ALSA | **REUSE** |

**Evidence**: The RK3326 datasheet specifies 2× I2S/PCM (2ch) and 1× I2S/TDM (8ch). The kernel config enables `CONFIG_SND_*` and Rockchip ASoC drivers. The `patches/alsa-ucm-conf/` directory contains audio configuration patches.

**Decision**: Core audio subsystem (kernel drivers, ASoC framework) is reusable. Speaker configuration, headphone jack routing, and any external codec differences require M9-specific DTS changes and UCM configuration.

---

## 5. BATTERY

| Aspect | R36S | M9 | Action |
|--------|------|-----|--------|
| Battery type | Li-polymer, ~3000-3200mAh | ??? | **REQUIRES M9 spec** |
| Battery driver | `simple-battery` | `simple-battery` | **REUSE** |
| Charge design | Varies per device (e.g., 2800000µAh for RGB10X) | ??? | **REQUIRES M9 spec** |
| Charge voltage | 4200mV (typical) | ??? | **REQUIRES M9 spec** |
| Power management | RK3326 PMU | RK3326 PMU | **REUSE** |
| Battery sysfs | `/sys/class/power_supply/` | Same | **REUSE** |
| Charge control | RK3326 PMU charge controller | Same | **REUSE** |
| USB charging | USB-C | USB-C (likely) | **REUSE** |

**Evidence**: `board/batocera/rockchip/rk3326/linux_patches/006-powkiddy-rgb10x.patch` shows the `battery` node with `charge-full-design-microamp-hours`, `charge-term-current-microamp`, `constant-charge-current-max-microamp`, `constant-charge-voltage-max-microvolt`. The `010-magicx-xu-mini-m.patch` shows battery capacity overrides for different devices. The R36S `batocera.conf.Game_Console_R36S` sets `system.suspendmode=suspend`.

**Decision**: The `simple-battery` driver and PMU framework are reusable. Battery capacity, charge parameters, and any PMU-specific quirks must be configured in the M9 DTS file based on the actual hardware.

---

## 6. Wi-Fi

| Aspect | R36S | M9 | Action |
|--------|------|-----|--------|
| Wi-Fi chip | ESP8089 or RTL8723BX | ??? | **REQUIRES M9 spec** |
| Wi-Fi driver | `esp8089` or `rtl8723bx` | ??? | **REQUIRES M9 spec** |
| Kernel patches | `008-esp-8089-wifi.patch`, `101-batocera-fix-esp8089-wifi.patch`, `1005-Bluetooth-btrtl-Add-the-support-for-RTL8733BU.patch` | Varies | **REQUIRES M9 spec** |
| SDIO quirks | `3000-mmc-add-rk915-wifi-cap2-flag.patch`, `3001-dw_mmc-rk915-cmd52-prv-dat-wait-and-no-lowpwr.patch`, `3002-sdio-cis-rk915-quirks.patch` | If RK915-based | **CONDITIONAL REUSE** |
| Firmware | `BR2_PACKAGE_FIRMWARE_ESP8089=y`, `BR2_PACKAGE_ARMBIAN_FIRMWARE_RTL8723BX=y` | ??? | **REQUIRES M9 spec** |
| Bluetooth | BT/BTLE | BT/BTLE | **CONDITIONAL** |
| Wi-Fi on/off switch | Physical switch (some models) | ??? | **REQUIRES M9 spec** |

**Evidence**: `configs/batocera-rk3326.board` enables `BR2_PACKAGE_FIRMWARE_ESP8089=y` and `BR2_PACKAGE_ARMBIAN_FIRMWARE_RTL8723BX=y`. The `linux_patches/` directory contains ESP8089 driver patches and RTL8733BU Bluetooth patches. The RK915 MMC patches (`3000-*`, `3001-*`, `3002-*`) indicate that some RK3326 boards use the RK915 Wi-Fi/BT combo chip on SDIO.

**Decision**: Wi-Fi subsystem is the **most device-dependent** component. If M9 uses ESP8089, the ESP8089 patches and firmware are reusable. If M9 uses RTL8723BX or RK915, different patches and firmware are needed. The MMC/SDIO quirks patches are conditional on the Wi-Fi chip used. **The M9 Wi-Fi chip identification is essential.**

---

## 7. LEDS

| Aspect | R36S | M9 | Action |
|--------|------|-----|--------|
| Power LED | GPIO-controlled | ??? | **REQUIRES M9 spec** |
| Button LEDs | RGB, GameForce-controlled via I2C | ??? | **REQUIRES M9 spec** |
| LED driver | `batocera-gameforce` | `batocera-gameforce` | **REUSE** (if GameForce I2C) |
| Init script | `S32colorbuttonled` (I2C GameForce) | ??? | **CONDITIONAL** |
| PWM LED | Possibly | ??? | **REQUIRES M9 spec** |

**Evidence**: `board/batocera/rockchip/rk3326/fsoverlay/etc/init.d/S32colorbuttonled` reads `/userdata/system/buttoncolorled.save` and `/userdata/system/powerled.save`, calling `batocera-gameforce "buttonColorLed"` and `batocera-gameforce "powerLed"`. The `patches/libretro-yabasanshiro/` and `patches/rockchip-rga/` directories contain related patches. `009-elida-refresh-rates.patch` references LED-related panel control.

**Decision**: If M9 uses the same GameForce I2C RGB LED controller as R36S, the init script and `batocera-gameforce` package are reusable. If M9 uses a different LED controller (e.g., simple GPIO LEDs, PWM, or a different I2C chip), a new init script and possibly new kernel patches are required.

---

## 8. USB

| Aspect | R36S | M9 | Action |
|--------|------|-----|--------|
| USB controller | RK3326 OTG (USB 2.0) | RK3326 OTG (USB 2.0) | **REUSE** |
| USB role | OTG with `usb-role-switch` | ??? | **CONDITIONAL** |
| USB-C port | USB-C charging + OTG | USB-C (likely) | **REUSE** |
| USB host | USB 2.0 Host | USB 2.0 Host | **REUSE** |
| USB gadgets | Serial/JTAG | Serial/JTAG | **REUSE** |
| USB PHY | RK3326 USB 2.0 PHY | Same | **REUSE** |
| USB driver | `CONFIG_USB_OTG`, `CONFIG_USB_DWC2` | Same | **REUSE** |

**Evidence**: `board/batocera/rockchip/rk3326/linux_patches/011-usb-role-switch.patch` adds `usb-role-switch` and `role-switch-default-mode = "host"` to the `px30.dtsi` USB OTG node. The RK3326 datasheet confirms one USB 2.0 OTG interface. Kernel config includes `CONFIG_USB_OTG`, `CONFIG_USB_DWC2`, `CONFIG_USB_NET_DRIVERS`, `CONFIG_USB_RTL8152`, etc.

**Decision**: USB subsystem is fully reusable at the kernel/driver level. The `usb-role-switch` patch may need to be re-applied to the M9 DTS file. If M9 has additional USB ports or different USB-C functionality, DTS changes may be needed.

---

## 9. STORAGE

| Aspect | R36S | M9 | Action |
|--------|------|-----|--------|
| eMMC | RK3326 eMMC controller | ??? | **REQUIRES M9 spec** |
| SD card | SDMMC controller | SDMMC controller | **REUSE** |
| SD card slots | Dual SD slots | ??? | **REQUIRES M9 spec** |
| SPI Flash | Boot SPI | Boot SPI | **REUSE** |
| NAND | NAND interface (not typically used) | N/A | **REUSE** |
| Storage layout | genimage.cfg: boot.vfat + userdata.ext4 | Same | **REUSE** |
| Boot partition | 16MB offset, 6GB FAT | Same | **REUSE** |
| Data partition | ext4, "SHARE" label, 512MB+ | Same | **REUSE** |
| Partition scheme | GPT/MBR | Same | **REUSE** |

**Evidence**: `board/batocera/rockchip/rk3326/r36s/genimage.cfg` defines the partition layout (idbloader, uboot, trust, vfat, userdata). `board/batocera/rockchip/rk3326/r36s/create-boot-script.sh` handles DTB copying and boot script generation. The kernel config includes `CONFIG_MMC`, `CONFIG_SDIO`, `CONFIG_MTD`, `CONFIG_SPI_NOR`.

**Decision**: Storage layout, partition scheme, and boot infrastructure are fully reusable. The DTS file must define M9-specific storage controllers (eMMC vs SDMMC vs SDIO). If M9 has dual SD slots, the DTS aliases and MMC node configuration must match.

---

## 10. POWER / ENERGIA

| Aspect | R36S | M9 | Action |
|--------|------|-----|--------|
| SoC power management | RK3326 PMU (ARM SCMI) | RK3326 PMU | **REUSE** |
| CPU DVFS | `ARM_SCPI_CPUFREQ` governor | Same | **REUSE** |
| CPU idle | ARM PSCI CPUIDLE | Same | **REUSE** |
| Suspend mode | `system.suspendmode=suspend` | ??? | **REQUIRES M9 spec** |
| Power button | GPIO-based | ??? | **REQUIRES M9 spec** |
| Battery charging | RK3326 PMU charge | Same | **REUSE** |
| Power off | PMU-controlled | Same | **REUSE** |
| Wake-up sources | GPIO, RTC | ??? | **REQUIRES M9 spec** |
| Battery sysfs | `/sys/class/power_supply/` | Same | **REUSE** |

**Evidence**: Kernel config shows `CONFIG_PM=y`, `CONFIG_SUSPEND=y`, `CONFIG_CPU_IDLE_GOV_LADDER=y`, `CONFIG_ARM_SCPI_PROTOCOL=y`, `CONFIG_ARM_PSCI_CPUIDLE=y`. `batocera.conf.Game_Console_R36S` sets `system.suspendmode=suspend`. The `batocera-system.mk` includes `SUSPEND_MODULES="rtw88_8822ce snd_pci_acp5x"`.

**Decision**: Power management framework is fully reusable. The suspend mode configuration, power button GPIO mapping, and wake-up source configuration must be specified in the M9 DTS and batocera.conf.

---

## 11. THERMAL

| Aspect | R36S | M9 | Action |
|--------|------|-----|--------|
| Thermal zones | RK3326 TSADC | RK3326 TSADC | **REUSE** |
| CPU thermal | TSADC-based | Same | **REUSE** |
| GPU thermal | `gpu-thermal` zone (from DTS) | Same | **REUSE** |
| Cooling | Passive cooling / active fan | ??? | **REQUIRES M9 spec** |
| Thermal trip points | Kernel default | Kernel default | **REUSE** |
| Fan control | ??? | ??? | **REQUIRES M9 spec** |

**Evidence**: `001-rk3326-dts.patch` adds `power_model@0` with `thermal-zone = "gpu-thermal"` for the GPU. The RK3326 datasheet includes TSADC (Temperature Sensor Analog-to-Digital Converter). Kernel config includes `CONFIG_THERMAL`, `CONFIG_ROCKCHIP_THERMAL`, `CONFIG_THERMAL_OF`, `CONFIG_CPU_THERMAL`.

**Decision**: Thermal subsystem (TSADC, thermal zones, GPU thermal model) is fully reusable. Any active cooling (fan) configuration or additional thermal zones must be added based on M9 hardware.

---

## 12. BOOT

| Aspect | R36S | M9 | Action |
|--------|------|-----|--------|
| Bootloader | U-Boot (Rockchip) | U-Boot (Rockchip) | **REUSE** |
| Boot ROM | RK3326 internal ROM | Same | **REUSE** |
| Boot device | SD card (MMC1) | SD card (likely) | **REUSE** |
| Boot script | `boot.ini` → `boot.scr` (U-Boot script) | New `boot.ini` | **CREATE** |
| DTB loading | `boot.ini` selects DTB via `hwrev` env | New DTB selection | **CREATE** |
| Kernel image | `Image` (arm64) | `Image` (arm64) | **REUSE** |
| Initramfs | `uInitrd` (lz4 compressed) | Same | **REUSE** |
| Genimage config | `genimage.cfg` (idbloader/uboot/trust/vfat/userdata) | Same | **REUSE** |
| Boot args | `label=BATOCERA console=ttyS2,1150000 console=tty3` | May differ | **CONDITIONAL** |
| Serial console | ttyS2 | ttyS2 (likely) | **REUSE** |
| U-Boot package | `uboot-odroid-goa` | May need different package | **CONDITIONAL** |
| SPL/idbloader | `idbloader.img` | Same format | **REUSE** |
| Trust firmware | `trust.img` | Same format | **REUSE** |
| DTB file | `rk3326-gameconsole-r36s.dtb` | New DTB needed | **CREATE** |
| Device Tree | `rk3326.dtsi` + `rk3326-linux.dtsi` + M9-specific | Same base | **REUSE + CREATE** |
| Boot overlays | `mipi-panel.dtbo` | New overlay(s) | **CREATE** |
| hwrev detection | U-Boot `hwrev` command | New hwrev ranges | **CREATE** |

**Evidence**: `board/batocera/rockchip/rk3326/r36s/boot/boot.ini` defines the boot flow with `hwrev` environment variable and DTB selection logic. `board/batocera/rockchip/rk3326/r36s/create-boot-script.sh` handles copying DTBs, kernel, initramfs, and generating boot.scr. `package/batocera/boot/uboot-odroid-goa/uboot-odroid-goa.mk` defines the U-Boot build. `package/batocera/boot/uboot-odroid-goa/007-hwrev-rg351v.patch` shows how hwrev detection is added to U-Boot.

**Decision**: The boot infrastructure (U-Boot, genimage, boot script framework) is reusable. The M9-specific `boot.ini` with hwrev detection, DTB file creation, and U-Boot hwrev patches must be created. Serial console and boot args likely remain the same.

---

## 13. FILESYSTEM / CONFIGURATION

| Aspect | R36S | M9 | Action |
|--------|------|-----|--------|
| Base config | `batocera.conf` (generic) | Generic base | **REUSE** |
| Board-specific conf | `sysconfigs/rk3326/batocera.conf.Game_Console_R36S` | New file | **CREATE** |
| Triggerhappy keys | `multimedia_keys_*.conf` | New file | **CREATE** |
| FSO overlay | `fsoverlay/etc/init.d/S32colorbuttonled`, `fsoverlay/etc/udev/rules.d/99-wifi-powersave.rules` | May differ | **CONDITIONAL** |
| Users table | `board/batocera/users.txt` | Same | **REUSE** |
| Buildroot config | `configs/batocera-rk3326.board` | New `batocera-rk3326-m9.board` | **CREATE** |
| Kernel defconfig | `board/batocera/rockchip/rk3326/linux-defconfig.config` | Same base | **REUSE** |
| Kernel fragment | `board/batocera/rockchip/rk3326/linux-defconfig-fragment.config` | Same base | **REUSE** |
| Kernel patches | `linux_patches/*.patch` | M9-specific subset | **CONDITIONAL** |
| Package configs | `package/batocera/core/batocera-system/Config.in` | Add `BR2_PACKAGE_BATOCERA_TARGET_RK3326_M9` | **CREATE** |

**Evidence**: The `sysconfigs/rk3326/` directory contains per-device `batocera.conf.*` files. The `batocera-triggerhappy/conf/rk3326/` directory contains per-device multimedia key mappings. `configs/batocera-rk3326.board` is the Buildroot configuration. `package/batocera/core/batocera-system/Config.in` contains the `BR2_PACKAGE_BATOCERA_TARGET_RK3326` Kconfig entry.

**Decision**: The generic configuration framework is reusable. Board-specific configuration files (batocera.conf, triggerhappy keys) and the Buildroot board config must be created for M9.

---

## SUMMARY TABLE

| Subsystem | Reuse from R36S | Replace from R36S | Create New | Depends on M9 Spec |
|-----------|----------------|-------------------|------------|-------------------|
| Display backend (Panfrost/LabWC) | ✅ 100% | — | — | No |
| GPU (Mali-G31 MP2, VPU) | ✅ 100% | — | — | No |
| Power management (PMU, DVFS) | ✅ 100% | — | — | No |
| USB (controller, drivers) | ✅ 100% | — | — | No |
| Storage layout (genimage, partitions) | ✅ 100% | — | — | No |
| Boot infrastructure (U-Boot, genimage) | ✅ 90% | `boot.ini` | DTB, hwrev | Yes |
| Thermal (TSADC, zones) | ✅ 100% | — | — | No |
| Audio (ASoC, drivers) | ✅ Kernel | Routing/config | UCM, DTS | Yes |
| LEDs (batocera-gameforce) | ✅ Framework | Init script | If different LED | Yes |
| Battery (simple-battery) | ✅ Driver | Charge params | DTS node | Yes |
| Joypad (rocknix-joypad) | ✅ Driver/arch | Button layout | DTSI, mappings | Yes |
| Wi-Fi (driver, firmware) | ⚠️ Conditional | Chip-specific | Driver, firmware | Yes |
| Display panel (DTS, overlays) | ⚠️ Framework | Panel config | DTS, DTBO | Yes |
| Board config (Buildroot) | ⚠️ Framework | Entire file | `.board`, Kconfig | Yes |
| Sysconfigs | ⚠️ Framework | Per-device files | batocera.conf, triggerhappy | Yes |
| Kernel DTS | ⚠️ Base files | Device-specific | M9 `.dts` + `.dtsi` | Yes |
| Kernel patches | ⚠️ Base patches | Chip-specific | M9-specific patches | Yes |
| U-Boot hwrev | ⚠️ Framework | hwrev ranges | hwrev patch | Yes |

---

## FILE LIST: REPOSITORY FILES LIKELY REQUIRING CHANGES

### Build Configuration
- `configs/batocera-rk3326-m9.board` — **CREATE** (new board config)
- `package/batocera/core/batocera-system/Config.in` — **MODIFY** (add `BR2_PACKAGE_BATOCERA_TARGET_RK3326_M9`)
- `package/batocera/core/batocera-system/batocera-system.mk` — **MODIFY** (add M9 arch mapping)

### Kernel Configuration
- `board/batocera/rockchip/rk3326/linux-defconfig.config` — **MAY NOT NEED** (shared base)
- `board/batocera/rockchip/rk3326/linux-defconfig-fragment.config` — **MAY NOT NEED** (shared base)

### Device Tree Source
- `board/batocera/rockchip/rk3326/dts/rk3326-m9-linux.dts` — **CREATE** (new DTS)
- `board/batocera/rockchip/rk3326/dts/rk3326-m9.dtsi` — **CREATE** (if needed)
- `board/batocera/rockchip/rk3326/dts/rk3326-m9-joypad.dtsi` — **CREATE** (if needed)
- `arch/arm64/boot/dts/rockchip/rk3326-m9-linux.dts` — **CREATE** (in-kernel DTS)
- `board/batocera/rockchip/rk3326/r36s/overlays/mipi-panel.dtbo.m9-*` — **CREATE** (panel overlays)

### Boot Configuration
- `board/batocera/rockchip/rk3326/m9/boot/boot.ini` — **CREATE**
- `board/batocera/rockchip/rk3326/m9/boot/create-boot-script.sh` — **CREATE** (or copy from r36s)
- `board/batocera/rockchip/rk3326/m9/genimage.cfg` — **CREATE** (copy from r36s)
- `board/batocera/rockchip/rk3326/m9/overlays/` — **CREATE** (copy base + M9-specific)

### Board Directory Structure
- `board/batocera/rockchip/rk3326/m9/` — **CREATE** (entire board directory)

### U-Boot
- `package/batocera/boot/uboot-odroid-goa/` — **MAY MODIFY** (if M9 uses same U-Boot)
- New U-Boot hwrev patch for M9 — **CREATE**
- `package/batocera/boot/uboot-rk3326/` — **MAY CREATE** if using mainline U-Boot

### Kernel Patches
- `board/batocera/rockchip/rk3326/linux_patches/` — **SELECTIVE** (reuse applicable patches, add M9-specific)

### Sysconfigs
- `package/batocera/core/batocera-system/sysconfigs/rk3326/batocera.conf.M9` — **CREATE**
- `package/batocera/core/batocera-triggerhappy/conf/rk3326/multimedia_keys_M9.conf` — **CREATE**

### FSO Overlay
- `board/batocera/rockchip/rk3326/m9/fsoverlay/etc/init.d/` — **CREATE** (LED scripts if different)
- `board/batocera/rockchip/rk3326/m9/fsoverlay/etc/udev/` — **CREATE** (Wi-Fi power save rules if different)

### System Packages
- `package/batocera/core/batocera-system/batocera.conf` — **MAY MODIFY** if new global options

### Configuration
- `configs/batocera-board.common` — **MAY NOT NEED** (shared)

### Documentation
- `batocera-Changelog.md` — **MODIFY** (add M9 entry)

---

## M9 HARDWARE INFORMATION NEEDED (BLOCKING)

Before any code can be written, the following M9 hardware specifications must be provided:

1. **Display**: Panel model, size, resolution, interface (MIPI/Parallel RGB/LVDS), lane count, controller IC
2. **Wi-Fi/BT**: Chip model (ESP8089, RTL8723BX, RK915, other), interface (SDIO/USB)
3. **Joypad**: Button layout, ADC channels, GPIO pins, stick type (analog/digital), PWM pins for rumble
4. **Audio**: Speaker configuration, headphone jack, any external codec
5. **Battery**: Capacity (mAh), charge voltage, charge current, PMU chip
6. **LEDs**: Power LED type/color, button LED controller (I2C address), PWM LED
7. **Storage**: eMMC present?, SD card slot count, SPI flash size
8. **USB**: Port count, USB-C functionality, any USB hub
9. **Power**: Power button GPIO, volume buttons (GPIO/scripted), wake-up sources
10. **Thermal**: Active cooling (fan?), additional thermal sensors
11. **U-Boot**: hwrev ADC ranges, boot device configuration
12. **Kernel version**: Target kernel version (R36S uses 6.18.16)
13. **Board revision**: Hardware version(s) to support

---

## EXECUTION ORDER (Once M9 Specs Are Available)

1. **Create board directory**: `board/batocera/rockchip/rk3326/m9/`
2. **Create Buildroot board config**: `configs/batocera-rk3326-m9.board`
3. **Create kernel DTS**: `arch/arm64/boot/dts/rockchip/rk3326-m9-linux.dts`
4. **Create boot scripts**: `board/batocera/rockchip/rk3326/m9/boot/`
5. **Create U-Boot hwrev patch**: Add M9 hwrev detection
6. **Create sysconfigs**: `batocera.conf.M9`, `multimedia_keys_M9.conf`
7. **Create FSO overlay**: Init scripts, udev rules
8. **Add Kconfig entry**: `BR2_PACKAGE_BATOCERA_TARGET_RK3326_M9` in `Config.in`
9. **Update batocera-system.mk**: Add M9 architecture mapping
10. **Create kernel patches**: M9-specific panel, joypad, Wi-Fi patches
11. **Update changelog**: Add M9 entry
