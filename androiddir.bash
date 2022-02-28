#!/bin/bash

# default Workspace dir, all projects are here
export defaultPath=~/zengjf/

# android project
projects=(
    M50-project
    A800-project
    M8-project
    L1400-project
)

# android product
products=(
    M50
    k61v1_64_bsp_pax
    k62v1_64_pax
    sc138
)

# android product kernel dir name, relative to project dir
kernels=(
    kernel-4.9
    kernel-4.9
    kernel-4.19
    android/kernel/msm-4.14
)

# android product kernel dts dir name
dtss=(
    arch/arm64/boot/dts/mediatek/
    arch/arm64/boot/dts/mediatek/
    arch/arm64/boot/dts/mediatek/
    arch/arm64/boot/dts/qcom
)

# android product bootloader stage 1th dir name, relative to project dir
#   1. mtk: preloader
#   2. qcom: xbl
bootloaderStage1s=(
    vendor/mediatek/proprietary/bootable/bootloader/preloader
    vendor/mediatek/proprietary/bootable/bootloader/preloader
    vendor/mediatek/proprietary/bootable/bootloader/preloader
    android/fibo/bp_code/boot_images
)

# android product bootloader stage 2th dir name, relative to project dir
#   1. mtk: lk
#   2. qcom: edk2
bootloaderStage2s=(
    vendor/mediatek/proprietary/bootable/bootloader/lk
    vendor/mediatek/proprietary/bootable/bootloader/lk
    vendor/mediatek/proprietary/bootable/bootloader/lk
    android/bootable/bootloader/edk2
)

# android product out dir, relative to project dir
outs=(
    out/target/product
    out/target/product
    out/target/product
    android/out/target/product
)

# for pp command alias
components=(
    android
    dts
    kernel
    out
    bs2
    bs1
)

# pp function
function project_product() {
    project=
    product=
    kernel=
    currentpath=`pwd`

    # jump command
    if [ $# -lt 1 ]; then
        for i in "${!projects[@]}"
        do
            echo $i: ${projects[i]} -- ${products[i]} -- ${kernels[i]}
        done

        echo
        cd $defaultPath
    elif [ $1 == "workspace" ]; then
        cd $defaultPath
    else

        # jump to project
        for i in "${!projects[@]}"
        do
            project_lowercase=${projects[i]%%-*}
            project_lowercase=${project_lowercase,,}
            if [ ${1,,} == "${project_lowercase}" ]; then
                project=${projects[i]}
                product=${products[i]}

                cd ${defaultPath}/${projects[i]}

                pwd

                if [ $# -eq 1 ]; then
                   return
                else
                   shift
                fi

                break
            fi
        done

        currentpath=`pwd`
        # jump to component
        for i in "${!projects[@]}"
        do
            if [[ ${currentpath} =~ "${projects[i]}" ]]; then
                project=${projects[i]}
                product=${products[i]}
                kernel=${kernels[i]}
                dts=${dtss[i]}
                bootloaderStage1=${bootloaderStage1s[i]}
                bootloaderStage2=${bootloaderStage2s[i]}
                out=${outs[i]}

                if [ $1 == "android" ]; then
                    cd ${defaultPath}/${project}
                elif [ $1 == "kernel" ]; then
                    cd ${defaultPath}/${project}/${kernel}
                elif [ $1 == "dts" ]; then
                    cd ${defaultPath}/${project}/${kernel}/${dts}
                elif [ $1 == "bs2" ]; then
                    cd ${defaultPath}/${project}/${bootloaderStage2}
                elif [ $1 == "bs1" ]; then
                    cd ${defaultPath}/${project}/${bootloaderStage1}
                elif [ $1 == "out" ]; then
                    cd ${defaultPath}/${project}/${out}/${product}
                else
                    return
                fi 

                break
            fi
        done

        if [ "${project}" == "" ]; then
            echo "please jump to your android project at first"
            cd ${defaultPath}
        fi
    fi
    pwd
}

# command alias
alias pp="project_product"   # just for project_product function alias
alias log="cd ~/log"         # just for log dir jump

# component alias
for i in "${!components[@]}"
do
    component=${components[i]}

    alias ${component}="project_product ${component}"
done

# project_product completion
projectStrings=""
componentStrings=""

function _project_product_completions()
{

    # get project string
    for i in "${!projects[@]}"
    do
        project_lowercase=${projects[i]%%-*}
        project_lowercase=${project_lowercase,,}

        projectStrings="${projectStrings} ${project_lowercase}"
    done

    # get project component string
    for i in "${!components[@]}"
    do
        component=${components[i]}
        componentStrings="${componentStrings} ${component}"
    done

    # completion
    if [ "${#COMP_WORDS[@]}" == "2" ]; then
        COMPREPLY=($(compgen -W "${projectStrings}" "${COMP_WORDS[1]}"))
    elif [ "${#COMP_WORDS[@]}" == "3" ]; then
        COMPREPLY=($(compgen -W "${componentStrings}" "${COMP_WORDS[2]}"))
    fi
}

complete -F _project_product_completions pp

# project completion
componentStrings=""

function _project_completions()
{

    # get project component string
    for i in "${!components[@]}"
    do
        component=${components[i]}
        componentStrings="${componentStrings} ${component}"
    done

    # completion
    if [ "${#COMP_WORDS[@]}" == "2" ]; then
        COMPREPLY=($(compgen -W "${componentStrings}" "${COMP_WORDS[1]}"))
    fi
}

# project alias and completion
for i in "${!projects[@]}"
do
    project_lowercase=${projects[i]%%-*}
    project_lowercase=${project_lowercase,,}

    alias ${project_lowercase}="project_product ${project_lowercase}"
    complete -F _project_completions ${project_lowercase}
done

