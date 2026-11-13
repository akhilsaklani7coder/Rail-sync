import os
import sys
import subprocess
import platform
import struct

def build_engine():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cpp_engine'))
    src_file = os.path.join(base_dir, 'core_logic.cpp')
    header_file = os.path.join(base_dir, 'core_logic.h')
    
    is_windows = platform.system() == 'Windows'
    out_name = 'railsync_engine.dll' if is_windows else 'librailsync_engine.so'
    out_file = os.path.join(base_dir, out_name)
    
    python_bits = struct.calcsize("P") * 8
    print(f"=== RailSync C++ Engine Build Utility ===")
    print(f"Host OS: {platform.system()} ({platform.machine()})")
    print(f"Target Python Architecture: {python_bits}-bit")
    print(f"Source: {src_file}")
    print(f"Output Target: {out_file}")

    # Check compilers
    candidate_compilers = [
        r'C:\Users\akhil\AppData\Local\Microsoft\WinGet\Packages\MartinStorsjo.LLVM-MinGW.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe\llvm-mingw-20260908-ucrt-x86_64\bin\g++.exe',
        'x86_64-w64-mingw32-g++',
        'g++',
        'clang++'
    ]
    chosen_compiler = None

    for comp in candidate_compilers:
        try:
            res = subprocess.run([comp, '--version'], capture_output=True, text=True, check=False)
            if res.returncode == 0:
                # Check if it produces 64-bit binaries
                test_cmd = [comp, '-dM', '-E', '-']
                test_res = subprocess.run(test_cmd, input='', capture_output=True, text=True, check=False)
                is_64 = '__x86_64__' in test_res.stdout or '_WIN64' in test_res.stdout
                print(f"Found compiler '{comp}': 64-bit mode={'YES' if is_64 else 'NO (32-bit only)'}")
                if is_64 or python_bits == 32:
                    chosen_compiler = comp
                    break
                elif not chosen_compiler:
                    chosen_compiler = comp  # fallback
        except (FileNotFoundError, OSError):
            continue

    if not chosen_compiler:
        print("\n[ERROR] No suitable C++ compiler (g++, clang++, or x86_64-w64-mingw32-g++) was found in PATH.")
        print("To install a 64-bit MinGW toolchain on Windows, run:")
        print("  winget install --id BrechtSanders.WinLibs.POSIX.UCRT -e")
        print("Or install Visual Studio Build Tools / MSYS2.\n")
        return False

    print(f"\nCompiling shared library with {chosen_compiler}...")
    cmd = [
        chosen_compiler,
        '-std=c++17',
        '-O3',
        '-shared',
        '-fPIC',
        '-static',
        '-static-libgcc',
        '-static-libstdc++',
        '-o', out_file,
        src_file
    ]

    cli_src = os.path.join(base_dir, 'engine_cli.cpp')
    cli_out = os.path.join(base_dir, 'engine_cli.exe' if is_windows else 'engine_cli')

    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[BUILD ERROR] Compilation of {out_name} failed:\n{res.stderr}")
            return False
        print(f"[SUCCESS] Compiled {out_name} successfully at {out_file}!")

        # Also compile engine_cli
        cmd_cli = [
            chosen_compiler,
            '-std=c++17',
            '-O3',
            '-static',
            '-static-libgcc',
            '-static-libstdc++',
            '-o', cli_out,
            cli_src,
            src_file
        ]
        res_cli = subprocess.run(cmd_cli, capture_output=True, text=True)
        if res_cli.returncode != 0:
            print(f"[BUILD WARNING] Compilation of engine_cli failed:\n{res_cli.stderr}")
        else:
            print(f"[SUCCESS] Compiled {os.path.basename(cli_out)} successfully at {cli_out}!")

        return True
    except Exception as e:
        print(f"[BUILD EXCEPTION] {e}")
        return False

if __name__ == '__main__':
    success = build_engine()
    sys.exit(0 if success else 1)
