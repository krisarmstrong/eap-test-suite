# Building `eapol_test` on macOS

**Author:** Kris Armstrong  
**Date:** March 7, 2025  
**License:** MIT License  

## **Overview**

This guide provides step-by-step instructions to successfully compile `eapol_test` on macOS, ensuring compatibility with macOS networking and OpenSSL 3.

---

## **🚀 Step 1: Install Required Dependencies**

Run the following command to install all necessary libraries:

```bash
brew install openssl libpcap libdnet pkg-config
```

### **Installed Packages**

- **`openssl`** → Provides TLS/SSL support
- **`libpcap`** → Required for macOS networking (`l2_packet_pcap.c`)
- **`libdnet`** → Provides `dnet.h`, needed by `l2_packet_pcap.c`
- **`pkg-config`** → Ensures correct paths for OpenSSL and dependencies

---

## **🚀 Step 2: Clone the Hostapd Repository**

Download the latest `hostapd` and `eapol_test` source code:

```bash
git clone git://w1.fi/srv/git/hostap.git
cd hostap/wpa_supplicant
```

---

## **🚀 Step 3: Create a `.config` File for macOS**

Run:

```bash
nano .config
```

Paste the following configuration:

```bash
CONFIG_EAPOL_TEST=y
CONFIG_TLS=openssl
CONFIG_TLSV11=y
CONFIG_TLSV12=y
CONFIG_TLSV13=y
CONFIG_TLS_FUNCS=y
CONFIG_OSX=y
CONFIG_L2_PACKET=pcap  # Use macOS-compatible networking

# OpenSSL paths (fix "openssl/ssl.h not found" errors)
CFLAGS += -I$(brew --prefix openssl)/include
LIBS += -L$(brew --prefix openssl)/lib -lssl -lcrypto

# libdnet paths (fix "dnet.h not found" errors)
CFLAGS += -I$(brew --prefix libdnet)/include
LIBS += -L$(brew --prefix libdnet)/lib -ldnet

# Enable all major EAP types
CONFIG_EAP_MD5=y
CONFIG_EAP_MSCHAPV2=y
CONFIG_EAP_TLS=y
CONFIG_EAP_PEAP=y
CONFIG_EAP_TTLS=y
CONFIG_EAP_FAST=y
CONFIG_EAP_PWD=y
CONFIG_EAP_LEAP=y
CONFIG_EAP_GPSK=y
CONFIG_EAP_PAX=y
CONFIG_EAP_SAKE=y
CONFIG_EAP_GTC=y
CONFIG_EAP_OTP=y
CONFIG_EAP_TNC=y
CONFIG_EAP_IKEV2=y

# SIM-based EAP authentication (for mobile networks)
CONFIG_EAP_SIM=y
CONFIG_EAP_AKA=y
CONFIG_EAP_AKA_PRIME=y

# Additional authentication options
CONFIG_PKCS12=y
CONFIG_SMARTCARD=y
CONFIG_PCSC=y
```

**Save & Exit**: `CTRL + X`, then `Y`, then `ENTER`

---

## **🚀 Step 4: Set Required Environment Variables**

Run:

```bash
export CFLAGS="-I$(brew --prefix openssl)/include -I$(brew --prefix libdnet)/include"
export LDFLAGS="-L$(brew --prefix openssl)/lib -L$(brew --prefix libdnet)/lib"
export PKG_CONFIG_PATH="$(brew --prefix openssl)/lib/pkgconfig:$(brew --prefix libdnet)/lib/pkgconfig"
export CPATH="$(brew --prefix openssl)/include:$(brew --prefix libdnet)/include"
```

---

## **🚀 Step 5: Modify Makefile to Use macOS Networking (`l2_packet_pcap.o` instead of Linux `l2_packet_linux.o`)**

By default, `eapol_test` tries to compile `l2_packet_linux.c`. We need to replace it with `l2_packet_pcap.o` for macOS.

Run:

```bash
nano ../src/l2_packet/Makefile
```

Find this line:

```make
l2_packet_linux.o
```

✅ **Replace it with:**

```make
l2_packet_pcap.o
```

Save and exit.

---

## **🚀 Step 6: Clean and Build**

Now, compile `eapol_test`:

```bash
make clean
make eapol_test
```

---

## **✅ Final Check: Verify `eapol_test` Works**

Once the build is complete, verify that `eapol_test` was created:

```bash
ls -l eapol_test
```

✅ If the binary **exists**, the build was successful.
❌ If there are any runtime issues, revisit the steps or troubleshoot based on any error messages.

To run `eapol_test`, use:

```bash
./eapol_test
```

---

## **🎯 Summary of Required Steps**

| **Step** | **Command** |
|-----------|------------|
| **1. Install required dependencies** | `brew install openssl libpcap libdnet pkg-config` |
| **2. Clone Hostapd repository** | `git clone git://w1.fi/srv/git/hostap.git && cd hostap/wpa_supplicant` |
| **3. Create `.config` for macOS** | *(See `.config` file above)* |
| **4. Set environment variables** | *(See export commands above)* |
| **5. Modify Makefile to use `l2_packet_pcap.o`** | *(See instructions above)* |
| **6. Build `eapol_test`** | `make clean && make eapol_test` |

---

## **🎉 Congratulations! `eapol_test` is Now Ready on macOS**

You have successfully built `eapol_test` on macOS! 🚀🔥

If you need further configuration, test it using:

```bash
./eapol_test
```

Let me know if you encounter any issues! 🎯

---

## **📜 License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
