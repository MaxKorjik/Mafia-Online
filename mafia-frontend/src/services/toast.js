import { useToast } from 'vue-toastification'

let toastInstance = null

export const getToast = () => {
  if (!toastInstance) {
    toastInstance = useToast()
  }
  return toastInstance
}

export const showError = (message) => {
  const toast = getToast()
  toast.error(message)
}

export const showSuccess = (message) => {
  const toast = getToast()
  toast.success(message)
}

export const showWarning = (message) => {
  const toast = getToast()
  toast.warning(message)
}

export const showInfo = (message) => {
  const toast = getToast()
  toast.info(message)
} 